import json
import glob
from sklearn.metrics import precision_score, recall_score, f1_score
import warnings

warnings.filterwarnings('ignore')  # "error", "ignore", "always", "default", "module" or "once"

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

        ont_rels += ont_rel + "(" + ont_domain + "," + ont_range + "),"

    return ont_rels[0:-1]


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
    example_prompt += "\nExample Output: " + train_sent['rel_label'] + "(" + train_sent['sub_label'] + "," + train_sent['obj_label'] + ")"
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

def get_test_ontology_string(ont_response_file,index):
    # extract substring from file name to get the ontology name
    start = ont_response_file.find('/')
    end = ont_response_file.find('llm', start+1)
    ont_name = ont_response_file[start+1:end]
    ont_name = ont_name + 'test_' + str(index)
    return ont_name

def get_ground_truth_file(ont_response_str):
    end = ont_response_str.find('_test')
    ont_ground_file = ont_response_str[0:end]

    return ont_ground_file


if __name__ == "__main__":

    path = 'src/ont_'
    ont_response_files = glob.glob(path + '*llm_responses.jsonl')
    prompts = []
    prompts_json = []

    i=0

    for ont_response_file in ont_response_files: #iterate through all the llm ontology response files
        i=i+1

        ont_response_file = ont_response_file.replace("\\", "/")
        print(f"1. ont_response_file == {ont_response_file}")
        ont_response_str = get_test_ontology_string(ont_response_file,i)
        ont_str = get_ontology_string(ont_response_str)

        print(f"1.1 ont_str == {ont_str}")

        print(f"2. ont_response_str=={ont_response_str}")
        ont_responses = load_jsonl(ont_response_file)
        x=0
        stats_json  = []
        for ont_response in ont_responses: #iterate through all the response entries in the response file
            #ont_response = get_ont_response_entry(ont_response_str, ont_responses)
            print(f"3. Ont_response== {ont_response}")
            ont_response_id = ont_response['id']
            triples = ont_response['triples']
            print(f"3.2 len(triples) = {len(triples)}")
            if len(triples) == 0:
                continue
            print(f"3.3 triples = {triples}")

            ont_ground_file = get_ground_truth_file(ont_response_str)
            path = 'src/data/ground_truth/' + ont_ground_file
            ont_ground_files = glob.glob(path + '*_ground_truth.jsonl')
            ont_ground_file = ont_ground_files[0].replace("\\", "/")
            print(f"4. ont_ground_file= {ont_ground_file}")
            ont_ground_truth_file = load_jsonl(ont_ground_file)
            ground_truth_entry = get_ground_truth_entry(ont_response_id, ont_ground_truth_file)
            print(f"5. ground_truth_entry= {ground_truth_entry}")
            ground_truth_id = ground_truth_entry['id']
            subject = ground_truth_entry['sub_label']
            predicate = ground_truth_entry['rel_label']
            object = ground_truth_entry['obj_label']
            ground_triple = [subject, predicate, object]  # it has only 1 triple x ground_truth entry
            # print(f"subject: {subject}, predicate: {predicate}, object: {object}")
            avg_precision, avg_recall, avg_f1 = 0,0,0

            for triple in triples:
                print(f"6. triple = {triple}")
                print(f"7. ground_triple: {ground_triple} vs triple: {triple}")
                y_true = triple
                y_pred = ground_triple

                precision = precision_score(y_true, y_pred, average='macro')
                avg_precision = precision + avg_precision
                recall = recall_score(y_true, y_pred, average='macro')
                avg_recall = recall + avg_recall
                f1 = f1_score(y_true, y_pred, average='macro')
                avg_f1 = f1 + avg_f1

                '''
                llm_triple = triple

                my_dict1={}
                my_dict1['id'] = ground_truth_id
                my_dict1['llm_triple'] = triple
                my_dict1['ground_triple'] = ground_triple
                my_dict1['precision'] = precision
                my_dict1['recall'] = recall
                my_dict1['f1'] = f1
                '''
                '''
                x=x+1
                if x==10:
                    exit(0)
                '''
            my_dict2 = {}
            my_dict2['id'] = ground_truth_id
            my_dict2['llm_triples'] = triples
            my_dict2['ground_triple'] = ground_triple

            res_prec = avg_precision / len(triples)
            res_prec = float('{0: .2f}'.format(res_prec))
            my_dict2['avg_precision'] = res_prec

            res_rec = avg_recall / len(triples)
            res_rec = float('{0: .2f}'.format(res_rec))
            my_dict2['avg_recall'] = res_rec

            res_f1 = avg_f1 / len(triples)
            res_f1 = float('{0: .2f}'.format(res_f1))
            my_dict2['avg_f1'] = res_f1

            #print(my_dict2)
            stats_json.append(my_dict2)

        print(f"=====>>>> len(stats_json == {len(stats_json)}")
        #exit(0)
        for elem in stats_json:
            # ont_1_movie_prompts.json
            path = "src/" + ont_str + '_llm_stats.json'

            with open(path, 'a+', encoding='utf-8') as f:
                json.dump(elem, f)
                f.write('\n')

        stats_json = []

        # print(f"8. id: {ground_truth_id} llm_triple: {triple} ground_triple: {ground_triple} Precision: {precision:.2f} Recall: {recall:.2f} F1 Score: {f1:.2f}")
