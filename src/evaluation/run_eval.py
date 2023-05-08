import argparse
import sys
import os
import json
import re
from typing import List, Dict, Set, Tuple
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

def read_jsonl(jsonl_path: str, is_json: bool = True) -> List:
    data = []
    with open(jsonl_path) as in_file:
        for line in in_file:
            if is_json:
                data.append(json.loads(line))
            else:
                data.append(line.strip())
    return data

def load_config(eval_config_path: str) -> Dict:
    raw_config = read_json(eval_config_path)
    onto_list = raw_config['onto_list']
    path_patterns = raw_config["path_patterns"]
    new_config = dict()
    expanded_onto_list = list()
    for onto in onto_list:
        onto_data = dict()
        onto_data["id"] = onto
        for key in path_patterns:
            onto_data[key] = path_patterns[key].replace("$$onto$$", onto)
        expanded_onto_list.append(onto_data)
    new_config["onto_list"] = expanded_onto_list
    new_config["avg_out_file"] = raw_config["avg_out_file"]
    return new_config

def save_jsonl(data: List, jsonl_path: str):
    with open(jsonl_path, "w") as out_file:
        for item in data:
            out_file.write(f"{json.dumps(item)}\n")

def append_jsonl(data: Dict, jsonl_path: str):
    with open(jsonl_path, "a+") as out_file:
        out_file.write(f"{json.dumps(data)}\n")

def read_json(json_path: str) -> Dict:
    with open(json_path) as in_file:
        return json.load(in_file)

def convert_to_dict(data: List[Dict], id_name: str = "id") -> Dict:
    return {item[id_name]: item for item in data}

def normalize_triple(sub_label, rel_label, obj_label):
    # remove spaces and make lower case
    sub_label = re.sub(r"(_|\s+)", '', sub_label).lower()
    rel_label = re.sub(r"(_|\s+)", '', rel_label).lower()
    obj_label = re.sub(r"(_|\s+)", '', obj_label).lower()
    # concatenate them to a single string
    tr_key = f"{sub_label}{rel_label}{obj_label}"
    return tr_key


def calculate_precision_recall_f1(gold: Set, pred: Set) -> (float, float, float):
    if len(pred) == 0:
        return 0, 0, 0
    p = len(gold.intersection(pred)) / len(pred)
    r = len(gold.intersection(pred)) / len(gold)
    if p + r > 0:
        f1 = 2 * ((p * r) / (p + r))
    else:
        f1 = 0
    return p, r, f1


def get_ontology_conformance(ontology: Dict, triples: List) -> (float, float):
    if len(triples) == 0:
        return 1, 0
    ont_rels = [rel['label'].replace(" ", "_") for rel in ontology['relations']]
    num_rels_conformant = len([tr for tr in triples if tr[1] in ont_rels])
    ont_conformance = num_rels_conformant / len(triples)
    rel_hallucination = 1 - ont_conformance
    return ont_conformance, rel_hallucination


def clean_entity_string(ps, entity: str):
    stemmed_entity = "".join([ps.stem(word) for word in word_tokenize(entity)])
    normalized_stemmed_entity = re.sub(r"(_|\s+)", '', stemmed_entity).lower()
    return normalized_stemmed_entity.replace("01januari", "")


def get_subject_object_hallucinations(ps, ontology, test_sentence, triples):
    if len(triples) == 0:
        return 0, 0
    test_sentence += " ".join([c["label"] for c in ontology['concepts']])
    stemmed_sentence = "".join([ps.stem(word) for word in word_tokenize(test_sentence)])
    normalized_stemmed_sentence = re.sub(r"(_|\s+)", '', stemmed_sentence).lower()

    num_subj_hallucinations, num_obj_hallucinations = 0, 0
    for triple in triples:
        normalized_stemmed_subject = clean_entity_string(ps, triple[0])
        normalized_stemmed_object = clean_entity_string(ps, triple[2])

        if normalized_stemmed_sentence.find(normalized_stemmed_subject) == -1:
            num_subj_hallucinations += 1
            #print(f"sub: {normalized_stemmed_sentence} - {normalized_stemmed_subject}")
        if normalized_stemmed_sentence.find(normalized_stemmed_object) == -1:
            num_obj_hallucinations += 1
            #print(f"obj: {normalized_stemmed_sentence} - {normalized_stemmed_object}")

    subj_hallucination = num_subj_hallucinations / len(triples)
    obj_hallucination = num_obj_hallucinations / len(triples)
    return subj_hallucination, obj_hallucination


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--eval_config_path', type=str, required=True)
    args = parser.parse_args()

    # stemmer for stemming words before checking for hallucinations
    ps = PorterStemmer()

    # load the files needed for evaluation from a user provided config file, it contains the system generated
    # output, the ground truth files, path to ontology file, and the path to store the evaluation output.
    eval_config_path = args.eval_config_path
    if not os.path.exists(eval_config_path):
        print(f"Evaluation config file is not found in path: {eval_config_path}")
    eval_inputs = load_config(eval_config_path)

    # evaluate the output of each of the ontologies
    for onto in eval_inputs['onto_list']:
        t_p, t_r, t_f1, t_onto_conf, t_rel_halluc, t_sub_halluc, t_obj_halluc = 0, 0, 0, 0, 0, 0, 0
        sel_t_p, sel_t_r, sel_t_f1, sel_t_onto_conf, sel_t_rel_halluc, sel_t_sub_halluc, sel_t_obj_halluc = \
            0, 0, 0, 0, 0, 0, 0
        eval_metrics_list = list()
        onto_id = onto['id']
        system_output = convert_to_dict(read_jsonl(onto['sys']))
        ground_truth = convert_to_dict(read_jsonl(onto['gt']))
        ontology = read_json(onto['onto'])
        if 'selected_ids' in onto:
            selected_ids = read_jsonl(onto['selected_ids'], is_json=False)
        else:
            selected_ids = []

        # iterate through each element in the ground truth and evaluate the system output
        for sent_id in list(ground_truth.keys()):
            # collect the ground truth triples
            gt_triples = [[tr['sub'], tr['rel'], tr['obj']] for tr in ground_truth[sent_id]['triples']]
            sentence = ground_truth[sent_id]["sent"]

            # check if system output as an entry for this sentence
            if sent_id in system_output:
                system_triples = system_output[sent_id]['triples']

                # collect the set of relations in ground truth triples, spaces are converted to "_" to make them
                # comparable with system triples
                gt_relations = {tr[1].replace(" ", "_") for tr in gt_triples}

                # filter out any triples in system output that does not match with ground truth relations
                filtered_system_triples = [tr for tr in system_triples if tr[1] in gt_relations]

                # create a normalized string from subject, relation, object of each triple for comparison
                normalized_system_triples = {normalize_triple(tr[0], tr[1], tr[2]) for tr in filtered_system_triples}
                normalized_gt_triples = {normalize_triple(tr[0], tr[1], tr[2]) for tr in gt_triples}

                # compare the system output with ground truth triples and calculate precision, recall, f1
                precision, recall, f1 = calculate_precision_recall_f1(normalized_gt_triples, normalized_system_triples)

                ont_conformance, rel_hallucination = get_ontology_conformance(ontology, system_triples)
                subj_hallucination, obj_hallucination = get_subject_object_hallucinations(ps, ontology, sentence,
                                                                                          system_triples)
                if  f1 < 1  and len(filtered_system_triples) > 0 and subj_hallucination == 0 and obj_hallucination == 0:
                    print(f"sent: {sentence}\nf1: {f1}\nsys:{filtered_system_triples}\nground:{gt_triples}\n\n")

                eval_metrics = {"id": sent_id, "precision": precision, "recall": recall, "f1": f1,
                                "onto_conf": ont_conformance, "rel_halluc": rel_hallucination,
                                "sub_halluc": subj_hallucination, "obj_halluc": obj_hallucination,
                                "llm_triples": system_triples, "filtered_llm_triples": filtered_system_triples,
                                "gt_triples": gt_triples, "sent": sentence}
                eval_metrics_list.append(eval_metrics)

                # aggregate precision, recall, f1 for later averaging
                t_p += precision
                t_r += recall
                t_f1 += f1
                t_onto_conf += ont_conformance
                t_rel_halluc += rel_hallucination
                t_sub_halluc += subj_hallucination
                t_obj_halluc += obj_hallucination

                # aggregate precision, recall, f1 for later averaging for selected ids
                if sent_id in selected_ids:
                    sel_t_p += precision
                    sel_t_r += recall
                    sel_t_f1 += f1
                    sel_t_onto_conf += ont_conformance
                    sel_t_rel_halluc += rel_hallucination
                    sel_t_sub_halluc += subj_hallucination
                    sel_t_obj_halluc += obj_hallucination

        save_jsonl(eval_metrics_list, onto['output'])
        total_test_cases = len(ground_truth)
        total_selected_test_cases = len(selected_ids)
        average_metrics = {"onto": onto_id, "type": "all_test_cases",
                           "avg_precision": f"{t_p/total_test_cases:.2f}",
                           "avg_recall": f"{t_r/total_test_cases:.2f}",
                           "avg_f1": f"{t_f1/total_test_cases:.2f}",
                           "avg_onto_conf": f"{t_onto_conf/total_test_cases:.2f}",
                           "avg_sub_halluc": f"{t_sub_halluc/total_test_cases:.2f}",
                           "avg_rel_halluc": f"{t_rel_halluc / total_test_cases:.2f}",
                           "avg_obj_halluc": f"{t_obj_halluc/total_test_cases:.2f}"
                           }
        append_jsonl(average_metrics, eval_inputs['avg_out_file'])
        if total_selected_test_cases > 0:
            selected_average_metrics = {"onto": onto_id, "type": "selected_test_cases",
                                        "avg_precision": f"{sel_t_p /total_selected_test_cases:.2f}",
                                        "avg_recall": f"{sel_t_r/total_selected_test_cases:.2f}",
                                        "avg_f1": f"{sel_t_f1/total_selected_test_cases:.2f}",
                                        "avg_onto_conf": f"{sel_t_onto_conf / total_selected_test_cases:.2f}",
                                        "avg_sub_halluc": f"{sel_t_sub_halluc / total_selected_test_cases:.2f}",
                                        "avg_rel_halluc": f"{sel_t_rel_halluc / total_selected_test_cases:.2f}",
                                        "avg_obj_halluc": f"{sel_t_obj_halluc / total_selected_test_cases:.2f}"}
            append_jsonl(selected_average_metrics, eval_inputs['avg_out_file'])


if __name__ == "__main__":
    sys.exit(main())