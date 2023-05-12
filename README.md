# Text2KG: A Benchmark for Ontology Driven Knowledge Graph Generation from Text
[![Code License](https://img.shields.io/badge/Code%20License-Apache_2.0-green.svg)](LICENSE)
[![Data License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)

This is the repository for ISWC 2023 Resource Track submission for `Text2KGBench: Benchmark for
Ontology-Driven Knowledge Graph Generation from Text`.
Text2KGBench is a benchmark to evaluate the capabilities of language models to generate KGs
from natural language text guided by an ontology. Given an input ontology and a set of sentences, the task is to extract facts from the text
while complying to the given ontology (concepts, relations, domain/range constraints) and being faithful to the input sentences.

It contains two datasets (i) Wikidata-TekGen with 10 ontologies and 13,474 sentences
and (ii) DBpedia-WebNLG with 19 ontologies and 4,860 sentences.

The data is released under under a Creative Commons Attribution-ShareAlike 4.0 International (CC BY 4.0) License.

The structure of the repo is as following.

- Text2KGBench
  - src: the source code used for generation and evaluation, and baseline
    - [`benchmark`](src/benchmark) the code used to generate the benchmark
    - [`evaluation`](src/evaluation) evaluation scripts for calculating the results
    - [baseline](src/evaluation) code for generating the baselines including prompts, sentence similarities, and LLM client.
  - data: the benchmark datasets and baseline data. There are two datasets: wikidata_tekgen and dbpedia_webnlg.
      - [wikidata_tekgen](data/wikidata_tekgen)
        - [ontologies](data/wikidata_tekgen/ontologies) 10 ontologies used by this dataset
        - [train](data/wikidata_tekgen/train) training data 
        - [test test data](data/wikidata_tekgen/test) test data 
        - [manually_verified_sentences](data/wikidata_tekgen/manually_verified_sentences) ids of a subset of test cases manually validated
        - [unseen_sentences](data/wikidata_tekgen/unseen_sentences) new sentences that are added by the authors which are not part of Wikipedia
          - test unseen test sentences 
          - ground_truth ground truth for unseen test sentecnes.
        - `ground_truth`ground truth for the test data
        - `baselines` data related to running the baselines.
          - `test_train_sent_similarity` for each test case, 5 most similar train sentences generated using SBERT T5-XXL model.
          - `prompts` prompts corresponding to each test file
            - `unseen` prompts for the unseen test cases
          - `Alpaca-LoRA-13B` data related to the Alpaca-LoRA model
            - `llm_responses` raw LLM responses and extracted triples 
            - `eval_metrics` ontology-level and aggregated evaluation results
            - `unseen` results for the unseen test cases
              - `llm_responses` raw LLM responses and extracte triples 
              - `eval_metrics` ontology-level and aggregated evaluation results
          - `Vicuna-13B` data related to the Vicuna-13B model
          - `llm_responses` raw LLM responses and extracted triples 
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
          - `Vicuna-13B` data related to the Vicuna-13B model
          - `llm_responses` raw LLM responses and extracted triples 
          - `eval_metrics` ontology-level and aggregated evaluation results     

This benchmark contains data derived from TekGen corpus (part of  the KELM corpus) [1] released under CC BY-SA 2.0 license
and WebNLG 3.0 corpus [2] released under CC BY-NC-SA 4.0 license.

[1] Oshin Agarwal, Heming Ge, Siamak Shakeri, and Rami Al-Rfou. 2021. Knowledge Graph Based Synthetic Corpus Generation 
for Knowledge-Enhanced Language Model Pre-training. In Proceedings of the 2021 Conference of the North American Chapter 
of the Association for Computational Linguistics: Human Language Technologies, pages 3554–3565, Online. 
Association for Computational Linguistics.

[2] Claire Gardent, Anastasia Shimorina, Shashi Narayan, and Laura Perez-Beltrachini. 2017. Creating Training Corpora 
for NLG Micro-Planners. In Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics 
(Volume 1: Long Papers), pages 179–188, Vancouver, Canada. Association for Computational Linguistics.

