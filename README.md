# Benchmark for Ontology Driven Knowledge Graph Generation from Text
Repository for ISWC 2023 Resource Track submission for Ontology Driven Knowledge Graph Generation from Text.




The structure of the repo is as following.

- Text2KG
  - src: the source code used for generation and evaluation, and baseline
    - [`benchmark`](src/benchmark) the code used to generate the benchmark
    - [`evaluation`](src/evaluation) evaluation scripts for calculating the results
    - [baseline](src/evaluation) code for generating the baselines including prompts, sentence similarities, and LLM client.
  - data: the benchmark datasets and baseline data. There are two datasets: wikidata_tekgen and dbpedia_webnlg.
      - [wikidata_tekgen](data/wikidata_tekgen)
        - [ontologies](data/wikidata_tekgen/ontologies) 10 ontologies used by this dataset
        - [train](data/wikidata_tekgen/train) training data 
        - `test`test data 
        - `selected_ids` a subset of test cases manually validated
        - `ground_truth`ground truth for the test data
        - `baselines` data related to running the baselines.
          - `test_train_sent_similarity` for each test case, 5 most similar train sentences generated using SBERT T5-XXL model.
          - `prompts` prompts corresponding to each test file
          - `Alpaca-LoRA-13B` data related to the Alpaca-LoRA model
            - `llm_responses` raw LLM responses and extracte triples 
            - `eval_metrics` ontology-level and aggregated evaluation results
           - `Vicuna-13B` data related to the Alpaca-LoRA model
            - `llm_responses` raw LLM responses and extracte triples 
            - `eval_metrics` ontology-level and aggregated evaluation results 
      - dbpedia_webnlg
        - `ontologies` 19 ontologies used by this dataset
        - `train` training data 
        - `test`test data 
        - `ground_truth`ground truth for the test data
        - `baselines` data related to running the baselines.
          - `test_train_sent_similarity` for each test case, 5 most similar train sentences generated using SBERT T5-XXL model.
          - `prompts` prompts corresponding to each test file
          - `Alpaca-LoRA-13B` data related to the Alpaca-LoRA model
            - `llm_responses` raw LLM responses and extracte triples 
            - `eval_metrics` ontology-level and aggregated evaluation results
           - `Vicuna-13B` data related to the Alpaca-LoRA model
            - `llm_responses` raw LLM responses and extracte triples 
            - `eval_metrics` ontology-level and aggregated evaluation results           
