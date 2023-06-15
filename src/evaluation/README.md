# Evaluation

## Evaluation config
For running the evaluation, you will need to create an evaluation script. Some examples can be found in the config directory.


```
{
  "onto_list" : [
    "1_movie",  "2_music", "3_sport", "4_book", "5_military", 
    "6_computer", "7_space", "8_politics", "9_nature", "10_culture"
  ],
  "path_patterns": {
    "sys": "../../data/wikidata_tekgen/baselines/Vicuna-13B/llm_responses/ont_$$onto$$_llm_responses.jsonl",
    "gt":"../../data/wikidata_tekgen/ground_truth/ont_$$onto$$_ground_truth.jsonl",
    "selected_ids": "../../data/wikidata_tekgen/manually_verified_sentences/selected_ont_$$onto$$.txt",
    "onto": "../../data/wikidata_tekgen/ontologies/$$onto$$_ontology.json",
    "output": "../../data/wikidata_tekgen/baselines/Vicuna-13B/eval_metrics/ont_$$onto$$_llm_stats_v2.jsonl"
  },
  "avg_out_file": "../../data/wikidata_tekgen/baselines/Vicuna-13B/eval_metrics/ont_llm_avg_stats_v2.jsonl"
}
```

## Running the evaluation script
In order to run the run_eval.py script we have to move to the Text2KGBench\src\evaluation directory:

*cd Text2KGBench\src\evaluation*

If we run the script with no parameters such as:
**python run_eval.py**

It will return the following response:
usage: run_eval.py [-h] --eval_config_path EVAL_CONFIG_PATH
run_eval.py: error: the following arguments are required: --eval_config_path

If we run the run_eval.py script with a --help parameter it will output the following response:
**python run_eval.py -h**

usage: run_eval.py [-h] --eval_config_path EVAL_CONFIG_PATH

options:
  -h, --help            show this help message and exit
  --eval_config_path EVAL_CONFIG_PATH

In the config directory (*cd config*) we find the following configuration files:

|14/06/2023|  16:59|              780 tekgen_vicuna_config.json|
|14/06/2023|  16:59|               684 tikgen_alpaca_config.json|
|14/06/2023|  16:59|               744 tikgen_unseen_alpaca_config.json|
|14/06/2023|  16:59|              729 tikgen_unseen_vicuna_config.json|
|14/06/2023|  16:59|               667 tikgen_vicuna_config.json|
|14/06/2023|  16:59|               916 webnlg_alpaca_config.json|
|14/06/2023|  16:59|               897 webnlg_vicuna_config.json|
               7 File(s)          5.417 bytes
 
Next, for running the run_eval.py script with a respective configuration file:
In this case we input the tekgen_vicuna_config.json with the following contents for example:

`
{
  "onto_list" : [
    "1_movie",  "2_music", "3_sport", "4_book", "5_military", "6_computer", "7_space", "8_politics", "9_nature", "10_culture"
  ],
  "path_patterns": {
    "sys": "../../data/wikidata_tekgen/baselines/Vicuna-13B/llm_responses/ont_$$onto$$_llm_responses.jsonl",
    "gt":"../../data/wikidata_tekgen/ground_truth/ont_$$onto$$_ground_truth.jsonl",
    "selected_ids": "../../data/wikidata_tekgen/manually_verified_sentences/selected_ont_$$onto$$.txt",
    "onto": "../../data/wikidata_tekgen/ontologies/$$onto$$_ontology.json",
    "output": "../../data/wikidata_tekgen/baselines/Vicuna-13B/eval_metrics/ont_$$onto$$_llm_stats_v2.jsonl"
  },
  "avg_out_file": "../../data/wikidata_tekgen/baselines/Vicuna-13B/eval_metrics/ont_llm_avg_stats_v2.jsonl"
}
`

Finally we run the run_eval.py script with a configuration file as parameter:
**python run_eval.py --eval_config_path config/tekgen_vicuna_config.json**

In this case the generated files can be found in the *"Text2KGBench\data\wikidata_tekgen\baselines\Vicuna-13B\eval_metrics"* directory:

15/06/2023  12:14           101.024 ont_10_culture_llm_stats_v2.jsonl
15/06/2023  12:14           833.962 ont_1_movie_llm_stats_v2.jsonl
15/06/2023  12:14           545.765 ont_2_music_llm_stats_v2.jsonl
15/06/2023  12:14           369.426 ont_3_sport_llm_stats_v2.jsonl
15/06/2023  12:14           394.056 ont_4_book_llm_stats_v2.jsonl
15/06/2023  12:14           166.479 ont_5_military_llm_stats_v2.jsonl
15/06/2023  12:14           165.176 ont_6_computer_llm_stats_v2.jsonl
15/06/2023  12:14           134.760 ont_7_space_llm_stats_v2.jsonl
15/06/2023  12:14           151.169 ont_8_politics_llm_stats_v2.jsonl
15/06/2023  12:14           264.178 ont_9_nature_llm_stats_v2.jsonl
15/06/2023  12:14             9.445 ont_llm_avg_stats_v2.jsonl
              11 File(s)      3.135.440 bytes
               0 Dir(s)  240.310.484.992 bytes free

Ten files are generated plus the total avg figures file. You may be able to view each file contents in your favourite editor.
