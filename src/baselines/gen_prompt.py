import json
import argparse
from typing import List


def get_ontology_concepts(ontology):
    """
    Generate a verbalized list of concepts in the given ontology to be included in the prompt
    :param ontology: an ontology as a dictionary
    :return: A string for ontology concepts.
             e.g. human, city, country, film, film genre....
    """
    ont_concepts = ""
    for onto in ontology['concepts']:
        ont_concepts += onto['label'] + ", "
    return ont_concepts[0:-1]


def get_concept_label(ontology, concept):
    """
    Get the label for the ontology concept
    :param ontology: ontology with concepts ids and labels
    :param ont_dom: input concept ID
    :return: the label of the input concept
    """
    for onto in ontology['concepts']:
        if onto['qid'] == concept:
            return onto['label']


def get_ontology_relations(ontology):
    """
    Generate a verbalized list of relations in the given ontology to be included in the prompt
    :param ontology:  an ontology as a dictionary
    :return: A string for ontology relations.
            e.g. cast_member(film,human), director (film,human), screenwriter(film,human), producer(film,human), ...
    """

    ont_rels = ""
    onto_rel_strings = list()
    for onto in ontology['relations']:
        ont_rel = onto['label']
        ont_rel = ont_rel.replace(" ", "_")
        ont_dom = onto['domain']
        ont_range = onto['range']
        ont_domain = get_concept_label(ontology, ont_dom)
        ont_range = get_concept_label(ontology, ont_range)

        if ont_rel == None:
            continue
        if ont_domain == None:
            ont_domain = ""
        if ont_range == None:
            ont_range = ""

        onto_rel_strings.append(f"{ont_rel} ({ont_domain},{ont_range})\n")

        ont_rels += ont_rel + "(" + ont_domain + "," + ont_range + "), "

    return ont_rels[0:-2]


def prepare_prompt(ontology: dict, test_sentence: str, train_sent: str) -> str:


    prompt_fixed = '''Given the following ontology and sentences, please extract the triples from the sentence according 
    to the relations in the ontology. In the output, only include the triples in the given output format. \n
'''

    prompt = prompt_fixed
    prompt += 'CONTEXT:\n\n'
    prompt += 'Ontology Concepts: '
    ont_concepts = get_ontology_concepts(ontology)
    prompt += ont_concepts
    prompt += '\nOntology Relations: '
    prompt += get_ontology_relations(ontology)
    prompt += get_example_prompt(train_sent)
    prompt += get_test_prompt(test_sentence)

    return prompt


def load_json(src_file):
    with open(src_file, 'r', encoding='utf-8') as f:
        source = json.load(f)
        return source


def load_jsonl(src_file):
    data = [json.loads(line) for line in open(src_file, 'r', encoding='utf-8')]
    return data


def save_jsonl(data: List, jsonl_path: str):
    with open(jsonl_path, "w") as out_file:
        for item in data:
            out_file.write(f"{json.dumps(item)}\n")


def get_similar_sentences(test_sentence_id, test_similar):
    for sim in test_similar:
        if sim == test_sentence_id:
            return test_similar[sim]


def get_train_sentence(simil_sent_id, train_sentences):
    for sent in train_sentences:
        if sent['id'] == simil_sent_id:
            return sent


def get_example_prompt(train_sent):
    example_prompt = "\n\nExample Sentence: " + train_sent['sent']
    train_sent['rel_label'] = train_sent['rel_label'].replace(" ", "_")
    example_prompt += "\nExample Output: " + train_sent['rel_label'] + "(" + train_sent['sub_label'] + "," + train_sent['obj_label'] + ")"
    return example_prompt


def get_test_prompt(test_sentence):
    test_prompt = "\n\nTest Sentence: " + test_sentence
    test_prompt += "\nTest Output: "
    return test_prompt


def get_ontology_string(ont_src_file):
    # extract substring from file name to get the ontology name
    start = ont_src_file.find('_')
    end = ont_src_file.find('_', start+1)
    ont_name = ont_src_file[start+1:end]
    return ont_name


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt_gen_config_path', type=str, required=True)
    args = parser.parse_args()
    prompt_gen_config_path = args.prompt_gen_config_path

    # load the prompt generation configuration with details of files needed for prompt generation
    # The config has a list of ontologies and patterns for generating for paths for the ontology file, test sentences
    # file, training sentences file, test-train sentence similarity file, and the output file.
    # Check wikidata_tekgen_unseen_prompt_gen_config.json for an example.
    prompt_gen_config = load_json(prompt_gen_config_path)
    prompts = []
    prompts_json = []
    onto_list = prompt_gen_config["onto_list"]

    # for each of the ontology, we load the corresponding files and generate the prompts for each test sentence
    for onto in onto_list:
        # load the ontology which has the concepts and relations (with domain / range constraints)
        ontology_file = prompt_gen_config["path_patterns"]["onto"].replace("$$onto$$", onto)
        ontology = load_json(ontology_file)

        # load the list of test sentences for which we need to generate the prompts.
        test_file = prompt_gen_config["path_patterns"]["test"].replace("$$onto$$", onto)
        test_sentences = load_jsonl(test_file)

        # load the list of train sentences. We use the train sentences with aligned triples to find the examples to
        # include in the prompt.
        train_file = prompt_gen_config["path_patterns"]["train"].replace("$$onto$$", onto)
        train_sentences = load_jsonl(train_file)

        # In the prompt, for each test sentence, we are using the most similar train sentence as the example for
        # in-context learning. This files contains pre-calculated similarities for each test sentence using a T5XXL
        # SBERT model.
        test_train_similarity_file = prompt_gen_config["path_patterns"]["sent_sim"].replace("$$onto$$", onto)
        test_train_similarity = load_json(test_train_similarity_file)

        # iterate through all test sentences while generating prompts
        for test_sentence in test_sentences:
            test_sentence_id = test_sentence['id']
            # test sentence for which the prompt to be generated
            test_sentence = test_sentence['sent']

            # get the similar train sentences for the test sentence
            similar_sents = get_similar_sentences(test_sentence_id, test_train_similarity)
            # we retrieve by default the first similar sentence from the list of similar sentences
            simil_sent_id = similar_sents[0]

            # we get the train sentence from the train sentences list and from there we process each field sub_label, obj_label, rel_label
            train_sent = get_train_sentence(simil_sent_id, train_sentences)

            # prompt generation logic
            prompt = prepare_prompt(ontology, test_sentence, train_sent)
            prompts.append(prompt)
            prompt_data = {'id': test_sentence_id, 'prompt': prompt}
            prompts_json.append(prompt_data)

        output_path = prompt_gen_config["path_patterns"]["prompt"].replace("$$onto$$", onto)
        save_jsonl(prompts_json, output_path)

        prompts_json = []
