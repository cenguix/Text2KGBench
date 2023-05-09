import json
import glob
from typing import List

def get_ontology_concepts(ontology):
    ont_concepts = ""
    for onto in ontology['concepts']:
        ont_concepts += onto['label'] + ", "
    return ont_concepts[0:-1]

def get_domain(ontology, ont_dom):
    for onto in ontology['concepts']:
        if onto['qid'] == ont_dom:
            return onto['label']

def get_range(ontology, ont_range):
    for onto in ontology['concepts']:
        if onto['qid'] == ont_range:
            return onto['label']

def get_ontology_relations(ontology):

    ont_rels = ""
    onto_rel_strings = list()
    for onto in ontology['relations']:
        ont_rel = onto['label']
        ont_rel = ont_rel.replace(" ", "_")
        ont_dom = onto['domain']
        ont_range = onto['range']
        ont_domain = get_domain(ontology, ont_dom)
        ont_range = get_range(ontology, ont_range)

        if ont_rel == None:
            continue
        if ont_domain == None:
            ont_domain = ""
        if ont_range == None:
            ont_range = ""

        onto_rel_strings.append(f"{ont_rel} ({ont_domain},{ont_range})\n")

        ont_rels += ont_rel + "(" + ont_domain + "," + ont_range + "), "

    return ont_rels[0:-2]


#def prepare_prompt(ontology: dict, test_sentence: str, train_sent: str, example_sentences: list[str]) -> str:
def prepare_prompt(ontology: dict, test_sentence: str, train_sent: str) -> str:

    prompt_fixed = '''Given the following ontology and sentences, please extract the triples from the sentence according 
    to the relations in the ontology. In the output, only include the triples in the given output format. \n
'''

    ## TODO generate the prompt
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


def find_similar_examples(test_sentence: str, train_sentences: list[str]) -> list[str]:
    pass

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

    prompt_gen_config = load_json("wikidata_tekgen_unseen_prompt_gen_config.json")
    prompts = []
    prompts_json = []
    onto_list = prompt_gen_config["onto_list"]

    i=0
    for onto in onto_list:
        #ont_src_file = ont_src_file.replace("\\","/")

        ontology_file = prompt_gen_config["path_patterns"]["onto"].replace("$$onto$$", onto)
        ontology = load_json(ontology_file) # loads the ontology
        print(len(ontology))

        test_file = prompt_gen_config["path_patterns"]["test"].replace("$$onto$$", onto)
        test_sentences = load_jsonl(test_file)

        train_file = prompt_gen_config["path_patterns"]["train"].replace("$$onto$$", onto)
        train_sentences = load_jsonl(train_file)


        test_train_similarity_file = prompt_gen_config["path_patterns"]["sent_sim"].replace("$$onto$$", onto)
        test_train_similarity = load_json(test_train_similarity_file)

        # iterate through all test sentences while generating prompts
        for test_sentence in test_sentences:
            test_sentence_id = test_sentence['id']
            test_sentence = test_sentence['sent'] # used later in prepare_prompt

            # get the similar sentences from the test similar source file
            similar_sents = get_similar_sentences(test_sentence_id, test_train_similarity)
            # we retrieve by default the first similar sentence from the list of similar sentences
            simil_sent_id = similar_sents[0]

            # we get the train sentence from the train sentences list and from there we process each field sub_label, obj_label, rel_label
            train_sent = get_train_sentence(simil_sent_id, train_sentences)

            prompt = prepare_prompt(ontology, test_sentence, train_sent)
            prompts.append(prompt)

            my_dict = {'id': '','prompt': ''}
            # my_dict['id'] = onto_id
            my_dict['id'] = test_sentence_id
            my_dict['prompt'] = prompt
            prompts_json.append(my_dict)

        output_path = prompt_gen_config["path_patterns"]["prompt"].replace("$$onto$$", onto)
        save_jsonl(prompts_json, output_path)

        prompts_json = []
