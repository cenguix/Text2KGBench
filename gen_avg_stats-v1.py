import json


def get_ontology_string(ont_stats_str_file):
    # extract substring from file name to get the ontology name
    start = ont_stats_str_file.find('ont')
    end = ont_stats_str_file.find('_llm')
    ont_name = ont_stats_str_file[start:end]
    return ont_name


def load_jsonl(src_file):
    data = [json.loads(line) for line in open(src_file, 'r', encoding='utf-8')]
    return data

def load_json(src_file):
    with open(src_file, 'r', encoding='utf-8') as f:
        source = json.load(f)
        return source

if __name__ == "__main__":

    path = 'src/ont_'
    #ont_response_files = glob.glob(path + '*llm_stats.json')
    ont_stat_files = ['src/ont_1_movie_llm_stats.jsonl', 'src/ont_2_music_llm_stats.jsonl', 'src/ont_3_sport_llm_stats.jsonl',
     'src/ont_4_book_llm_stats.jsonl', 'src/ont_5_military_llm_stats.jsonl', 'src/ont_6_computer_llm_stats.jsonl', 'src/ont_7_space_llm_stats.jsonl',
     'src/ont_8_politics_llm_stats.jsonl', 'src/ont_9_nature_llm_stats.jsonl', 'src/ont_10_culture_llm_stats.jsonl']
    prompts = []
    prompts_json = []

    i = 0
    print(ont_stat_files)
    stats_json = []
    for ont_stat_file in ont_stat_files:  # iterate through all the llm ontology response files

        ont_str = get_ontology_string(ont_stat_file)
        ont_stat_id = ont_str  #+ '_avg_stats'
        print(f"ont_str {ont_str}")
        #exit(0)
        ont_stats = load_jsonl(ont_stat_file)
        #print(f"len ont_stats {len(ont_stats)}")

        avg_precision = 0
        avg_recall = 0
        avg_f1 = 0
        avg_ont_conformance = 0
        avg_ont_rel_hallucinations = 0
        avg_ont_subj_hallucinations = 0
        avg_ont_obj_hallucinations = 0

        for ont_stat in ont_stats:
            avg_precision = ont_stat['precision'] + avg_precision
            avg_recall = ont_stat['recall'] + avg_recall
            avg_f1 = ont_stat['f1'] + avg_f1
            avg_ont_conformance = ont_stat['ont_conformance'] + avg_ont_conformance
            avg_ont_rel_hallucinations = ont_stat['ont_rel_hallucinations'] + avg_ont_rel_hallucinations
            avg_ont_subj_hallucinations = ont_stat['ont_subj_hallucinations'] + avg_ont_subj_hallucinations
            avg_ont_obj_hallucinations = ont_stat['ont_obj_hallucinations'] + avg_ont_obj_hallucinations

        avg_precision = float('{0: .2f}'.format(avg_precision / len(ont_stats)))
        avg_recall = float('{0: .2f}'.format(avg_recall / len(ont_stats)))
        avg_f1 = float('{0: .2f}'.format(avg_f1 / len(ont_stats)))
        avg_ont_conformance = float('{0: .2f}'.format(avg_ont_conformance / len(ont_stats)))
        avg_ont_rel_hallucinations = float('{0: .2f}'.format(avg_ont_rel_hallucinations / len(ont_stats)))
        avg_ont_subj_hallucinations = float('{0: .2f}'.format(avg_ont_subj_hallucinations / len(ont_stats)))
        avg_ont_obj_hallucinations = float('{0: .2f}'.format(avg_ont_obj_hallucinations / len(ont_stats)))

        my_dict = {}
        my_dict['id'] = ont_stat_id

        my_dict['P'] = avg_precision
        my_dict['R'] = avg_recall
        my_dict['F1'] = avg_f1
        my_dict['Ont_Conf'] = avg_ont_conformance
        my_dict['Ont_Subj_Halluci'] = avg_ont_subj_hallucinations
        my_dict['Ont_Rel_Halluci'] = avg_ont_rel_hallucinations
        my_dict['Ont_Obj_Halluci'] = avg_ont_obj_hallucinations

        #print(f"avg_precision {avg_precision}")
        #print(f"avg_recall {avg_recall}")
        #print(f"avg_f1 {avg_f1}")
        #print(f"avg_ont_conformance {avg_ont_conformance}")
        #print(f"avg_ont_rel_hallucinations {avg_ont_rel_hallucinations}")
        #print(f"avg_ont_subj_hallucinations {avg_ont_subj_hallucinations}")
        #print(f"avg_ont_obj_hallucinations {avg_ont_obj_hallucinations}")

        stats_json.append(my_dict)
        # exit(0)

    for elem in stats_json:
        # ont_1_movie_prompts.json
        path = 'src/ont_llm_avg_stats.jsonl'

        with open(path, 'a+', encoding='utf-8') as f:
            json.dump(elem, f)
            f.write('\n')

