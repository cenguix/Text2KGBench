# Evaluation

## Evaluation config
For running the evaluation, you will need to create an evaluation script. Some examples can be found in the [config directory](config). Each test suite such as Wikidata_Tekgen or DBpedia_WebNLG contains set of ontologies and the config file contains parametrized path patterns to files corresponding to each ontology in the test suite.  

The following shows one example.

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
    "output": "../../data/wikidata_tekgen/baselines/Vicuna-13B/eval_metrics/ont_$$onto$$_llm_stats.jsonl"
  },
  "avg_out_file": "../../data/wikidata_tekgen/baselines/Vicuna-13B/eval_metrics/ont_llm_avg_stats.jsonl"
}
```

Here are the description of each of the paramters in the config.

| Parameter                  | Description                                                                                                    |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| onto_list                  | List of ids of ontologies. These are used for converting file path patterns to absolute paths.                 |
| path_patterns/sys          | The path pattern to system outputs for test sentences in each ontology.                                        |
| path_patterns/gt           | The path pattern to ground truth triples for each ontology.                                                    |
| path_patterns/selected_ids | (Optional) The path pattern to a selected list of manually validated test cases if applicable.                 |
| path_patterns/onto         | The path pattern to the ontology file.                                                                         |
| path_patterns/output       | The path pattern for the detailed output file with metrics for each individual test sentence in each ontology. |
| avg_out_file               | The path pattern for average metrics at ontology level and globally for the whole dataset.                     |



## Running the evaluation script
In order to run the run_eval.py script we have to move to the Text2KGBench\src\evaluation directory:
```
cd Text2KGBench\src\evaluation
```
Here we propose working initially with the wikidata_tekgen dataset and the baseline model Vicuna13B

If we run the script with no parameters such as:
```
python run_eval.py
```
It will return the following response:
> usage: run_eval.py [-h] --eval_config_path EVAL_CONFIG_PATH
> 
> run_eval.py: error: the following arguments are required: --eval_config_path

If we run the **run_eval.py** script with a --help parameter it will output the following response:
```
python run_eval.py -h
```
> usage: run_eval.py [-h] --eval_config_path EVAL_CONFIG_PATH
>
> options:
> 
>  -h, --help            show this help message and exit
>  
>  --eval_config_path EVAL_CONFIG_PATH

In the config directory (**cd config**) we find the following configuration files:

|Date      |  Time |  Bytes          | File                     |
|----------|-------|-----------------|--------------------------|
|14/06/2023|  16:59|              780| tekgen_vicuna_config.json|
|14/06/2023|  16:59|               684| tikgen_alpaca_config.json|
|14/06/2023|  16:59|               744| tikgen_unseen_alpaca_config.json|
|14/06/2023|  16:59|              729 |tikgen_unseen_vicuna_config.json|
|14/06/2023|  16:59|               667| tikgen_vicuna_config.json|
|14/06/2023|  16:59|               916 |webnlg_alpaca_config.json|
|14/06/2023|  16:59|               897 |webnlg_vicuna_config.json|
 
Next, for running the run_eval.py script with a respective configuration file:
In this case we will specify the input configuration file as **tekgen_vicuna_config.json** which has the following contents:

```
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
```

Finally we run the **run_eval.py** script with a configuration file as parameter:
```
python run_eval.py --eval_config_path config/tekgen_vicuna_config.json
```
In this case the generated files can be found in the *"Text2KGBench\data\wikidata_tekgen\baselines\Vicuna-13B\eval_metrics"* directory as indicated in the previous configuration file (*avg_out_file entry*):
|Date      |  Time |  Bytes          | File                     |
|----------|-------|-----------------|--------------------------|
15/06/2023 | 12:14 |          101.024| ont_10_culture_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |           833.962| ont_1_movie_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |         545.765| ont_2_music_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |          369.426| ont_3_sport_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |           394.056| ont_4_book_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |          166.479| ont_5_military_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |          165.176| ont_6_computer_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |          134.760| ont_7_space_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |          151.169| ont_8_politics_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |          264.178| ont_9_nature_llm_stats_v2.jsonl|
15/06/2023 | 12:14 |            9.445| ont_llm_avg_stats_v2.jsonl|
               
Ten files are generated plus the total avg figures file. You may be able to view each file contents in your favourite text editor.

Each generated file contains the following entries:
* **id**: the ontology test identifier i.e. "ont_1_movie_test_1" 
* **precision**: precision metrics P = correct_triples/predicted_triples
* **recall**: recall metrics R = correct_triples/gold_triples
* **f1**: F1 score metrics F1 = harmonic mean of precision and recall. F1 = 2 * ((P * R) / (P + R)).
* **onto_conf (OC)**: ontology conformance (OC) metrics which is the number of system triple relations in the ontology divided by the total number of system triples  
* **rel_halluc (RH)**: relation hallucination (RH) metrics which it is inversely related to OC and equal to RH = 1 - OC which is the number of system triple relations that are not in the ontology divided by the total number of system triples  
* **sub_halluc (SH)**: subject hallucination (SH) metrics calculated by checking if pre-processed triple subject is referred in the test sentence and/or ontology concepts 
* **obj_halluc (OH)**: object hallucination (OH) metrics checking if pre-processed triple object is referred in the test sentence  and/or ontology concepts
* **llm_triples**: LLM system triples i.e. [["Bleach: Hell Verse", "director", "Noriyuki Abe"]] 
* **filtered_llm_triples**: filtered LLM triples i.e. [["Bleach: Hell Verse", "director", "Noriyuki Abe"]]
* **gt_triples**: ground truth triples i.e. [["Bleach : Hell Verse", "director", "Noriyuki Abe"], ["Bleach : Hell Verse", "publication date", "01 January 2010"]], 
* **sent**: original test sentence for extracting facts i.e. "Bleach: Hell Verse (Japanese: BLEACH , Hepburn: Bur\u00c4\u00abchi Jigoku-Hen) is a 2010 Japanese animated film directed by Noriyuki Abe."}

The total avg metrics file contains the following fields:
* **onto**: the ontology identifier i.e. "1_movie", 
* **type**: type of average calculation either *"all_test_cases"* or *"selected_test_cases"* or *"global(global average figures)"*
* **avg_precision (AP)**: total average precision for the ontology
* **avg_recall (AR)**: total average recall for the ontology
* **avg_f1 (AF1)**: total average F1 score for the ontology
* **avg_onto_conf (AOC)**: total average ontology conformance for the ontology
* **avg_sub_halluc (ASH)**: total average subject hallucination metrics for the ontology
* **avg_rel_halluc (ARH)**: total average relation hallucination metrics for the ontology ARH = 1 - AOC
* **avg_obj_halluc (AOH)**: total average object hallucination metrics for the ontology
