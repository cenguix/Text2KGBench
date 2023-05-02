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

def get_avg_prec_rec_f1(ground_triple, triples_with_rel, abs_num_triples):

    avg_precision = 0
    avg_recall = 0
    avg_f1 = 0

    for triple in triples_with_rel:
        y_true = triple
        y_pred = ground_triple

        precision = precision_score(y_true, y_pred, average='macro')
        avg_precision = precision + avg_precision
        recall = recall_score(y_true, y_pred, average='macro')
        avg_recall = recall + avg_recall
        f1 = f1_score(y_true, y_pred, average='macro')
        avg_f1 = f1 + avg_f1

    avg_precision = avg_precision/abs_num_triples
    avg_recall = avg_recall/abs_num_triples
    avg_f1 = avg_f1/abs_num_triples

    return avg_precision, avg_recall, avg_f1


def get_precision_recall_f1(triples, ground_triple):

    precision = 0
    recall = 0
    f1 = 0

    # if there are no triples in the response, then precision, recall, f1 are all 0
    if len(triples) == 0:
        return precision, recall, f1

    triples_with_rel = []
    num_triples_with_rel = 0

    for triple in triples:
        if triple[1] == ground_triple[1]:
            num_triples_with_rel+=1
            triples_with_rel.append(triple)
    # No relation in system output - Recall: 0, Precision: 0, F1: 0
    if num_triples_with_rel == 0:
        precision, recall, f1 = 0, 0, 0
        return precision, recall, f1
    elif num_triples_with_rel == 1:
        #there is one relation and it is correct - Recall: 1, Precision: 1, F1: 1
        if ground_triple in triples:
            precision, recall, f1 = 1, 1, 1
            return precision, recall, f1
        else: #there is one relation and it is not correct either subject or object triple - Recall: 1, Precision: 0, F1: 0
            precision, recall, f1 = 0, 1, 0
            return precision, recall, f1
    elif num_triples_with_rel > 1:
        #there are more than one relation and one of them is correct: Recall: 1, Precision: 0.P (< 1.0) , F1:
        if ground_triple in triples:
            precision, recall, f1 = get_avg_prec_rec_f1(ground_triple, triples_with_rel, len(triples))
            recall = 1
            return precision, recall, f1
        else: #there are more than one relation and none of them is correct: Recall: 0, Precision: 0 , F1: 0
            precision, recall, f1 = 0, 0, 0
            return precision, recall, f1


def get_ontology_conformance(ont_str, triples, i):
    #ont_1_movie
    start = ont_str.find('_')
    start = ont_str.find('_',start+1)
    ont = ont_str[start+1:]
    ont_file = 'src/ontology/' + str(i) + '_' + ont + '_ontology.json'
    ontology = load_json(ont_file)

    num_rels_conformant = 0
    num_rel_hallucinations = 0

    ont_rels = get_ont_rels(ontology)

    for triple in triples:
        if triple[1] in ont_rels:
            print(f"kk1{triple[1]} kk1{ont_rels}")
            num_rels_conformant = num_rels_conformant + 1
        else:
            num_rel_hallucinations = num_rel_hallucinations + 1
            print("1")

    ont_conformance = num_rels_conformant/len(triples)

    return ont_conformance, num_rel_hallucinations


def get_ont_rels(ontology):

    ont_rels = []

    for onto in ontology['relations']:
        ont_rel = onto['label']
        ont_rel = ont_rel.replace(" ", "_")

        if ont_rel == None:
            continue

        ont_rels.append(ont_rel)

    return ont_rels

def get_ontology_hallucinations(test_sentence_id, ont_str, triples, i):

    # the test source file respective to the ontology
    path = "src/data/" +  ont_str + "/" +  ont_str + "_test.jsonl"
    print(path)

    # test_src = glob.glob(path + '/*test*.jsonl')
    # test_src = test_src[0].replace("\\", "/")
    #print(test_src)

    test_sentences = load_jsonl(path)

    # by default we only use the first sentence in the test set but we should iterate over all of them (there are > 800)
    for test_sentence in test_sentences:
        if test_sentence['id'] == test_sentence_id:
            test_sentence = test_sentence['sent']  # get the required sentence
            break

    num_subj_hallucinations = 0
    num_obj_hallucinations = 0
    for triple in triples:
        subj = triple[0]
        obj = triple[2]
        if test_sentence.find(subj) == -1:
            print(f"kk9{subj} kk1{test_sentence}")
            num_subj_hallucinations = num_subj_hallucinations + 1
        if test_sentence.find(obj) == -1:
            print(f"kk10{triple[1]} kk1{test_sentence}")
            num_obj_hallucinations = num_obj_hallucinations + 1

    return num_subj_hallucinations, num_obj_hallucinations


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
        exit(0)
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

            ont_conformance, ont_rel_hallucinations = get_ontology_conformance(ont_str, triples, i)
            print(f"ont_conformance= {ont_conformance}, ont_rel_hallucinations= {ont_rel_hallucinations}")
            ont_response_id = ont_response['id']
            ont_subj_hallucinations, ont_obj_hallucinations = get_ontology_hallucinations(ont_response_id, ont_str, triples, i)
            print(f"ont_subj_hallucinations= {ont_subj_hallucinations}, ont_obj_hallucinations= {ont_obj_hallucinations}")

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

            precision, recall, f1 = get_precision_recall_f1(triples, ground_triple)
            #print(f"precision: {precision}, recall: {recall}, f1: {f1}")
            '''
            x=x+1
            if x==100:
                exit(0)
            
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

                llm_triple = triple

                my_dict1={}
                my_dict1['id'] = ground_truth_id
                my_dict1['llm_triple'] = triple
                my_dict1['ground_triple'] = ground_triple
                my_dict1['precision'] = precision
                my_dict1['recall'] = recall
                my_dict1['f1'] = f1
                x=x+1
                if x==10:
                    exit(0)
            '''
            '''
            x=x+1
            if x==8:
                exit(0)
            '''
            my_dict = {}
            my_dict['id'] = ground_truth_id
            my_dict['llm_triples'] = triples
            my_dict['ground_triple'] = ground_triple

            my_dict['precision'] = float('{0: .2f}'.format(precision))
            my_dict['recall'] = float('{0: .2f}'.format(recall))
            my_dict['f1'] = float('{0: .2f}'.format(f1))
            my_dict['ont_conformance'] = float('{0: .2f}'.format(ont_conformance))
            my_dict['ont_rel_hallucinations'] = float('{0: .2f}'.format(ont_rel_hallucinations))
            my_dict['ont_subj_hallucinations'] = float('{0: .2f}'.format(ont_subj_hallucinations))
            my_dict['ont_obj_hallucinations'] = float('{0: .2f}'.format(ont_obj_hallucinations))
            print(f"my_dict {my_dict}")

            stats_json.append(my_dict)

        print(f"=====>>>> len(stats_json == {len(stats_json)}")
        #exit(0)
        for elem in stats_json:
            # ont_1_movie_prompts.json
            path = "src/" + ont_str + '_llm_stats.json'

            with open(path, 'a+', encoding='utf-8') as f:
                json.dump(elem, f)
                f.write('\n')

        stats_json = []
