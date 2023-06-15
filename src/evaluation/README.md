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
