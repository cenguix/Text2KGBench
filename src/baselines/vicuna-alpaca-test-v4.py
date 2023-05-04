# Simple toy example of how to use Vicuna and Alpaca models
import copy
from llama_cpp import Llama
import time


sentences = ["A Gang Story (French: Les Lyonnais) is a 2011 French drama film directed by Olivier Marchal.",
            "Released in Italy in 1964 and then in the United States in 1967, A Fistful of Dollars initiated the popularity of the Spaghetti Western genre.",
            "The Dark Knight Rises is a 2012 superhero film directed by Christopher Nolan, who co-wrote the screenplay with his brother Jonathan Nolan, and the story with David S. Goyer."]

sentence_context = ["Visions of Light is a 1992 documentary film directed by Arnold Glassman, Todd McCarthy and Stuart Samuels.",
                    "Visions of Light film genre is Science and Documentary",
                    "The Visions of Light film screenplay was done by Quentin Tarantino and John Travolta"]

correct_answers = ["director(Visions of Light, Arnold Glassman) \ndirector(Visions of Light, Todd McCarthy) \ndirector(Visions of Light, Stuart Samuels)",
                    "genre(Visions of Light, Science)\ngenre(Visions of Light, Documentary)",
                    "screenplay(Visions of Light, Quentin Tarantino)\nscreenplay(Visions of Light, John Travolta)"]

print("Loading model...")
start_time = time.time()
#llm = Llama(model_path="./models/ggml-vicuna-13b-4bit-rev1.bin") #vicuna model
#llm = Llama(model_path="./models/gpt4-x-alpaca-13b-native-ggml-q4_0.bin") #alpaca model 1
llm = Llama(model_path="./models/ggml-toolpaca-13b-4bit.bin") #alpaca model 2
end_time= time.time()
print(f"Model loading time: {end_time-start_time}")

# standard prompt
prompt="""
Given the following ontology and sentence, please extract the triples from the sentence according to the relations in the ontology. 
In the output, only include the triples in the given output format: relation(subject, object) 

context:  
Ontology Concepts: film, film genre, film production company, film award, city, human
Ontology relations: director(film, human), genre(film, film genre), cast member(film, human)

Sentence:
"""
#Here we add sentence_context[i] to the prompt

correct_answer_text="\nCorrect Answer:\n"

#Here we add correct_answers[i]

sent_text = "\nGiven this sentence: "
# Here we add sentences[i]

answer="""
Give the correct answer
Answer:
"""

for i in range(len(sentences)):
    #print(sentences[i])
    prompt_sentence = ""
    prompt_sentence = prompt + sentence_context[i]
    prompt_sentence += correct_answer_text + correct_answers[i]
    prompt_sentence += sent_text + sentences[i] + answer
    #print(prompt_sentence)

    #propmt sent to the LLM
    start_time = time.time()
    # max_tokens = 512 for alpaca model if you surpass this limit you will get an error
    output = llm(prompt_sentence, max_tokens=250, echo=True, temperature=0)
    end_time = time.time()
    print(f"Query LLM loading time: {end_time - start_time}")
    text = output["choices"][0]["text"]

    #Extract the answer from the output
    start_pos = text.find("Give the correct answer\nAnswer:")
    start_pos = start_pos + len("Give the correct answer\nAnswer:")
    #print("Question:")
    #print(text[:start_pos])
    print(f"Answer: {text[start_pos:]}")

