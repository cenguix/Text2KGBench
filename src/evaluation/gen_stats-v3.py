import json
import re
import glob
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import warnings
import nltk
nltk.download('punkt')

warnings.filterwarnings('ignore')  # "error", "ignore", "always", "default", "module" or "once"


def get_ontology_concepts(ontology):
    ont_concepts = ""
    for onto in ontology['concepts']:
        ont_concepts += onto['label'] + ","
    return ont_concepts[0:-1]


def get_domain(ontology, ont_dom):
    for onto in ontology['concepts']:
        if onto['qid'] == ont_dom:
            return onto['label']


def get_range(ontology, ont_range):
    for onto in ontology['concepts']:
        if onto['qid'] == ont_range:
            return onto['label']

def load_json(src_file):
    with open(src_file, 'r', encoding='utf-8') as f:
        source = json.load(f)
        return source


def load_jsonl(src_file):
    data = [json.loads(line) for line in open(src_file, 'r', encoding='utf-8')]
    return data


def get_similar_sentences(test_sentence_id, test_similar):
    for sim in test_similar:
        if sim == test_sentence_id:
            return test_similar[sim]


def get_train_sentence(simil_sent_id, train_sentences):
    for sent in train_sentences:
        if sent['id'] == simil_sent_id:
            return sent


def get_ground_truth_entry(ont_response_id, ont_ground_truth_file):
    for ground_truth in ont_ground_truth_file:
        if ground_truth['id'] == ont_response_id:
            return ground_truth


def get_ont_response_entry(ont_response_str, ont_responses):
    for response in ont_responses:
        if response['id'] == ont_response_str:
            return response


def get_example_prompt(train_sent):
    example_prompt = "\n\nExample Sentence: " + train_sent['sent']
    train_sent['rel_label'] = train_sent['rel_label'].replace(" ", "_")
    example_prompt += "\nExample Output: " + train_sent['rel_label'] + "(" + train_sent['sub_label'] + "," + train_sent[
        'obj_label'] + ")"
    return example_prompt


def get_test_prompt(test_sentence):
    test_prompt = "\n\nTest Sentence: " + test_sentence
    test_prompt += "\nTest Output: "
    return test_prompt


def get_ontology_string(ont_response_str):
    # extract substring from file name to get the ontology name
    end = ont_response_str.find('_test')
    ont_name = ont_response_str[0:end]
    return ont_name


def get_test_ontology_string(ont_response_file, index):
    # extract substring from file name to get the ontology name
    start = ont_response_file.find('/')
    end = ont_response_file.find('llm', start + 1)
    ont_name = ont_response_file[start + 1:end]
    ont_name = ont_name + 'test_' + str(index)
    return ont_name


def get_ground_truth_file(ont_response_str):
    end = ont_response_str.find('_test')
    ont_ground_file = ont_response_str[0:end]

    return ont_ground_file


def calculate_precision_recall_f1(llm_triples, ground_triples):

    if len(llm_triples) == 0:
        return 0, 0, 0
    #print("INSIDE llm triples: ", llm_triples)
    #print("INSIDE ground triples: ", ground_triples)
    # preprocess llm triples
    llm_triples = get_llm_triple_processed(llm_triples)
    #print("INSIDE ======>0 llm triples: ", llm_triples)
    llm_triples = {normalized_triple_string(triple) for triple in llm_triples}

    ground_triples = get_ground_triple_processed(ground_triples)
    #print("INSIDE ===>>> 1 ground triples: ", ground_triples)
    ground_triples = {normalized_triple_string(triple) for triple in ground_triples}
    #print("INSIDE ===>>> 2 TUPLE ground triples: ", ground_triples)
    ground_triples = set(ground_triples)
    #print("@@@SET ground triples: ", ground_triples)
    llm_triples = set(llm_triples)
    #print("@@@SET llm triples: ", llm_triples)

    p = len(ground_triples.intersection(llm_triples)) / len(llm_triples)
    if (len(ground_triples) == 0):
        r = 0
    else:
        r = len(ground_triples.intersection(llm_triples)) / len(ground_triples)

    if p + r > 0:
        f1 = 2 * ((p * r) / (p + r))
    else:
        f1 = 0

    return p, r, f1

def get_llm_triple_processed(triples):

    llm_triples = []
    for triple in triples:
        llm_triple = [None, None, None]
        triple = remove_leading_under_score_space(triple, 0)
        triple = remove_leading_under_score_space(triple, 1)
        triple = remove_leading_under_score_space(triple, 2)

        subj = get_stemmed_sentence(triple[0])
        subj = subj.replace(" ", "").lower()

        #rel = get_stemmed_sentence(triple[1])
        rel = triple[1]
        rel = rel.replace(" ", "").lower()

        obj = get_stemmed_sentence(triple[2])
        obj = obj.replace(" ", "").lower()

        llm_triple = [subj, rel, obj]
        llm_triples.append(llm_triple)

    return llm_triples


def get_ground_triple_processed(ground_triples):
    triples_converted = []

    for ground_triple in ground_triples:
        triple = [None, None, None]
        #print(f"LOOP ground_triple: {ground_triple}")
        subj = get_stemmed_sentence(ground_triple['sub'])

        #@subj = ground_triple['sub']
        subj = subj.replace(" ", "").lower()

        rel = ground_triple['rel']
        # if rel starts with underscore or space remove it
        if rel.startswith("_") or rel.startswith(" "):
            rel = rel[1:]
        #if more than 1 word in rel, replace space with underscore
        rel = rel.replace(" ", "_")
        #print(f"rel after replace underscore: {rel}")
        #rel = get_stemmed_sentence(rel)
        #print(f"rel after stemmed: {rel}")
        #@rel = rel.replace(" ", "").lower()
        #print(f"rel after replace space: {rel}")

        obj = get_stemmed_sentence(ground_triple['obj'])
        #@obj = ground_triple['obj']
        obj = obj.replace(" ", "").lower()

        #print(f"triple: {triple}")
        triple=[subj, rel, obj]
        #print(f"END LOOP ground_triple: {triple}")
        triples_converted.append(triple)
        #print(f"END LOOP triple_converted: {triples_converted}")
    #print(f"triples_converted: {triples_converted}")
    return triples_converted


def normalized_triple_string(triple):
    # remove spaces and make lower case
    sub_label = re.sub(r"(_|\s+)", '', triple[0]).lower()
    rel_label = re.sub(r"(_|\s+)", '', triple[1]).lower()
    obj_label = re.sub(r"(_|\s+)", '', triple[2]).lower()
    # concatenate them
    tr_key = f"{sub_label}{rel_label}{obj_label}"
    return tr_key


def get_ontology_conformance(ontology, triples):
    num_rels_conformant = 0
    num_rel_hallucinations = 0

    ont_rels = get_ont_rels(ontology)

    for triple in triples:
        #print(f"Before triple: {triple}")
        triple = remove_leading_under_score_space(triple,1)
        #print(f"After triple: {triple}")
        #exit(0)
        if triple[1] in ont_rels:
            #print(f"kk1{triple[1]} kk1{ont_rels}")
            num_rels_conformant = num_rels_conformant + 1
        else:
            num_rel_hallucinations = num_rel_hallucinations + 1
            #print("1")

    ont_conformance = num_rels_conformant / len(triples)
    num_rel_hallucinations = num_rel_hallucinations / len(triples)

    return ont_conformance, num_rel_hallucinations


def remove_leading_under_score_space(triple, i): # remove leading underscore and space

    if triple[i].startswith("_"):
        triple[i] = triple[i].replace("_", "")
    elif triple[i].startswith(" "):
        triple[i] = triple[1].replace(" ", "")

    return triple


def get_ont_rels(ontology):
    ont_rels = []

    for onto in ontology['relations']:
        ont_rel = onto['label']
        if ont_rel.startswith('_') or ont_rel.startswith(' '):
            ont_rel = ont_rel[1:]

        ont_rel = ont_rel.replace(" ", "_")

        if ont_rel == None:
            continue

        ont_rels.append(ont_rel)

    return ont_rels


def get_ontology_hallucinations(test_sentence_id, test_sentence, triples, i):

    # test_src = glob.glob(path + '/*test*.jsonl')
    # test_src = test_src[0].replace("\\", "/")
    # print(test_src)

    test_before = test_sentence
    test_sentence = get_stemmed_sentence(test_sentence)
    test_sentence = test_sentence.replace(" ", "").lower()

    num_subj_hallucinations = 0
    num_obj_hallucinations = 0
    for triple in triples:
        triple = remove_leading_under_score_space(triple, 0)
        triple = remove_leading_under_score_space(triple, 2)

        subj = triple[0]
        obj = triple[2]

        subj = get_stemmed_sentence(subj)
        subj = subj.replace(" ", "").lower()
        obj = get_stemmed_sentence(obj)
        obj = obj.replace(" ", "").lower()
        #print(f"==>SUBJ {subj} OBJ {obj} TEST_SENTENCE {test_sentence}")
        if test_sentence.find(subj) == -1:
            #print(f"kk9{subj} kk1{test_sentence}")
            num_subj_hallucinations = num_subj_hallucinations + 1
        if test_sentence.find(obj) == -1:
            #print(f"kk10{triple[1]} kk1{test_sentence}")
            num_obj_hallucinations = num_obj_hallucinations + 1

    num_subj_hallucinations = num_subj_hallucinations / len(triples)
    num_obj_hallucinations = num_obj_hallucinations / len(triples)

    return num_subj_hallucinations, num_obj_hallucinations


def get_stemmed_sentence(test_sentence):

    words = word_tokenize(test_sentence)
    word_sentences = []
    for w in words:
        word_sentences.append(ps.stem(w))

    sentence = ' '.join(word_sentences)

    return sentence



if __name__ == "__main__":

    ps = PorterStemmer()
    #TODO load these from a config file or from command line
    evaluation_input_params = [
        [
            '../../data/ground_truth/ont_1_movie_ground_truth_v1.jsonl',
            '../../data/baselines/vicuna_13B/llm_responses/ont_1_movie_llm_responses_v2.jsonl',
            '../../data/ontology/1_movie_ontology.json',
            '../../data/baselines/vicuna_13B/eval/ont_1_movie_llm_stats.jsonl'
        ]
    ]
        # 'src/ont_2_music_llm_responses_v2.jsonl',
        # 'src/ont_3_sport_llm_responses_v2.jsonl',
        # 'src/ont_4_book_llm_responses_v2.jsonl',
        # 'src/ont_5_military_llm_responses_v2.jsonl',
        # 'src/ont_6_computer_llm_responses_v2.jsonl',
        # 'src/ont_7_space_llm_responses_v2.jsonl',
        # 'src/ont_8_politics_llm_responses_v2.jsonl',
        # 'src/ont_9_nature_llm_responses_v2.jsonl',
        # 'src/ont_10_culture_llm_responses_v2.jsonl']

    prompts = []
    prompts_json = []

    i = 0

    for input_params in evaluation_input_params:  # iterate through all the llm ontology response files
        i = i + 1

        ground_truth_file = input_params[0]
        llm_response_file = input_params[1]
        ontology_file = input_params[2]
        output_file = input_params[3]
        onto_id = ontology_file.split("/")[-1].replace("_ontology.json", "")

        #ont_response_file = ont_response_file.replace("\\", "/")
        #print(f"1. ont_response_file == {ont_response_file}")
        # ont_response_str = get_test_ontology_string(ont_response_file, i)
        # ont_str = get_ontology_string(ont_response_str)

        #print(f"1.1 ont_str == {ont_str}")

        #print(f"2. ont_response_str=={ont_response_str}")
        ont_responses = load_jsonl(llm_response_file)
        ontology = load_json(ontology_file)
        ont_ground_truth = load_jsonl(ground_truth_file)
        test_id_to_sent = {gt['id']: gt['sent'] for gt in ont_ground_truth}

        x = 0
        stats_json = []
        total_p, total_r, total_f1, total_ont_conf, total_sh, total_rh, total_oh = 0, 0, 0, 0, 0, 0, 0
        for ont_response in ont_responses:  # iterate through all the response entries in the response file
            # ont_response = get_ont_response_entry(ont_response_str, ont_responses)
            #print(f"3. Ont_response== {ont_response}")
            ont_response_id = ont_response['id']
            triples = ont_response['triples']
            print(f"3.2 len(triples) = {len(triples)}")
            if len(triples) == 0:
                continue

            ont_conformance, ont_rel_hallucinations = get_ontology_conformance(ontology, triples)
            total_ont_conf += ont_conformance
            total_rh += ont_rel_hallucinations
            print(f"ont_conformance= {ont_conformance}, ont_rel_hallucinations= {ont_rel_hallucinations}")
            ont_response_id = ont_response['id']
            sent = test_id_to_sent[ont_response_id]
            ont_subj_hallucinations, ont_obj_hallucinations = get_ontology_hallucinations(ont_response_id, sent,triples, i)
            total_sh += ont_rel_hallucinations
            total_oh += ont_rel_hallucinations
            print(f"ont_subj_hallucinations= {ont_subj_hallucinations}, ont_obj_hallucinations= {ont_obj_hallucinations}")

            #print(f"3.3 triples = {triples}")

            # ont_ground_file = get_ground_truth_file(ont_response_str)
            # path = 'src/data/ground_truth/' + ont_ground_file
            # ont_ground_files = glob.glob(path + '*_ground_truth_v1.jsonl')
            # ont_ground_file = ont_ground_files[0].replace("\\", "/")
            # #print(f"4. ont_ground_file= {ont_ground_file}")
            ground_truth_entry = get_ground_truth_entry(ont_response_id, ont_ground_truth)
            #print(f"5. ground_truth_entry= {ground_truth_entry}")

            ground_truth_id = ground_truth_entry['id']
            ground_triples = ground_truth_entry['triples']
            #ground_triples = get_processed_ground_triples(ground_triples)
            #print(f"5.1 ground_triples = {ground_triples}")

            #precision, recall, f1 = get_precision_recall_f1(triples, ground_triples)

            precision, recall, f1 = calculate_precision_recall_f1(triples, ground_triples)
            total_p += precision
            total_r += recall
            total_f1 += f1
            print(f"precision: {precision}, recall: {recall}, f1: {f1}")
            '''
            x=x+1
            if x==100:
                exit(0)
            '''
            my_dict = {}
            my_dict['id'] = ground_truth_id
            my_dict['llm_triples'] = triples
            my_dict['ground_triples'] = ground_triples

            my_dict['precision'] = float('{0: .2f}'.format(precision))
            my_dict['recall'] = float('{0: .2f}'.format(recall))
            my_dict['f1'] = float('{0: .2f}'.format(f1))
            my_dict['ont_conformance'] = float('{0: .2f}'.format(ont_conformance))
            my_dict['ont_rel_hallucinations'] = float('{0: .2f}'.format(ont_rel_hallucinations))
            my_dict['ont_subj_hallucinations'] = float('{0: .2f}'.format(ont_subj_hallucinations))
            my_dict['ont_obj_hallucinations'] = float('{0: .2f}'.format(ont_obj_hallucinations))
            print(f"20. my_dict {my_dict}")

            stats_json.append(my_dict)
        #exit(0)
        print(f"=====>>>> len(stats_json) == {len(stats_json)}")
        print(f"tf: {total_p}")

        avg_metrics = {}
        avg_metrics['id'] = onto_id
        avg_metrics['P'] = (total_p / len(ont_ground_truth))
        avg_metrics['R'] = total_r / len(ont_ground_truth)
        avg_metrics['F1'] = total_f1 / len(ont_ground_truth)
        avg_metrics['Ont_Conf'] = total_ont_conf / len(ont_ground_truth)
        avg_metrics['Ont_Subj_Halluci'] = total_sh / len(ont_ground_truth)
        avg_metrics['Ont_Rel_Halluci'] = total_rh / len(ont_ground_truth)
        avg_metrics['Ont_Obj_Halluci'] = total_oh / len(ont_ground_truth)

        with open(output_file, "w") as output_file:
            for elem in stats_json:
                output_file.write(f"{json.dumps(elem)}\n")

        with open('../../data/baselines/vicuna_13B/eval/ont_llm_avg_stats.jsonl', 'a+') as output_file:
            output_file.write(f"{json.dumps(avg_metrics)}\n")

        stats_json = []
        #exit(0)