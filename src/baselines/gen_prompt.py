import json
import glob

'''
def get_llm_response(prompt: str) -> str:
    data = { "model": "vicuna-13b", "messages": [{"role": "user", "content": prompt}] }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url=completion_url, headers=headers, data=json.dumps(data))
    return response.json()['choices'][0]['message']['content']

def parse_llm_response(response: str) -> List[Triple]:
    # TODO return triples in the form of "subject, relation, object"
    pass
'''

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

        ont_rels += ont_rel + "(" + ont_domain + "," + ont_range + "), "

    return ont_rels[0:-2]


#def prepare_prompt(ontology: dict, test_sentence: str, train_sent: str, example_sentences: list[str]) -> str:
def prepare_prompt(ontology: dict, test_sentence: str, train_sent: str) -> str:

    prompt_fixed = '''
Given the following ontology and sentences, please extract the triples from the sentence according to the relations in the ontology. In the output, only include the triples in the given output format.
'''

    ## TODO generate the prompt
    prompt = prompt_fixed
    prompt += 'CONTEXT:\n'
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

    # the ontology source file should iterate over all of them movie ontology, music ontology, etc.
    path= "../../data/ontology"
    prompts = []
    prompts_json = []
    ont_files = glob.glob(path + '/*.json')
    #temp solution for testing
    ont_files = ['ontology/1_movie_ontology.json', 'ontology/2_music_ontology.json', 'ontology/3_sport_ontology.json', 'ontology/4_book_ontology.json', 'ontology/5_military_ontology.json',
     'ontology/6_computer_ontology.json', 'ontology/7_space_ontology.json', 'ontology/8_politics_ontology.json', 'ontology/9_nature_ontology.json', 'ontology/10_culture_ontology.json' ]
    print(ont_files)

    i=0
    for ont_src_file in ont_files:
        #ont_src_file = ont_src_file.replace("\\","/")

        i=i+1
        ont = get_ontology_string(ont_src_file)
        print(ont)
        ontology = load_json(ont_src_file) # loads the ontology movie, music, sports, etc.
        print(len(ontology))

        onto_id = "ont_" + str(i) + "_" + ont + "_test_" + str(i) # this field is used for the output json prompt file

        # the test source file respective to the ontology
        path = "data/ont_" + str(i) + "_" + ont
        print(path)

        test_src = glob.glob(path + '/*test*.jsonl')
        test_src = test_src[0].replace("\\","/")
        print(test_src)

        test_sentences = load_jsonl(test_src)

        #by default we only use the first sentence in the test set but we should iterate over all of them (there are > 800)
        for test_sentence in test_sentences:
            test_sentence_id = test_sentence['id']

            test_sentence = test_sentence['sent'] # used later in prepare_prompt

            # the test similar source file generated with sbert might include movie ontology, music ontology, etc.
            path = 'baselines/sbert_example_similarity/ont_' + str(i) + '_' + ont + '_'

            test_similar_src = glob.glob(path + '*similarity.json')
            if test_similar_src == []:
                print("No more ontologies to process.")
                break

            test_similar_src = test_similar_src[0].replace("\\","/")
            #test_similar_src = "baselines/sbert_example_similarity/ont_1_movie_test_train_similarity.json"
            test_similar = load_json(test_similar_src)

            # get the similar sentences from the test similar source file
            similar_sents = get_similar_sentences(test_sentence_id, test_similar)
            # we retrieve by default the first similar sentence from the list of similar sentences
            simil_sent_id = similar_sents[0]

            # we retrieve the train sentence from the train source file
            path = "data/ont_" + str(i) + "_" + ont + '/ont_' + str(i) + '_' + ont + '_'

            train_src = glob.glob(path + '*train.jsonl')
            train_src = train_src[0].replace("\\", "/")
            train_sentences = load_jsonl(train_src)
            # we get the train sentence from the train sentences list and from there we process each field sub_label, obj_label, rel_label
            train_sent = get_train_sentence(simil_sent_id, train_sentences)

            prompt = prepare_prompt(ontology, test_sentence, train_sent)
            prompts.append(prompt)

            my_dict = {'id': '','prompt': ''}
            # my_dict['id'] = onto_id
            my_dict['id'] = test_sentence_id
            my_dict['prompt'] = prompt
            prompts_json.append(my_dict)

        #print(len(prompts_json))

        for elem in prompts_json:
            #ont_1_movie_prompts.json
            path = 'ont_' + str(i) +  '_' + ont + '_prompts.json'
            with open(path, 'a+', encoding='utf-8' ) as f:
                json.dump(elem, f)
                f.write('\n')

        prompts_json = []
