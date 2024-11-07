# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# NLP libraries
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
#nltk.download('punkt')
#nltk.download('wordnet')
#nltk.download('omw-1.4')
#nltk.download('stopwords')

import spacy
from spacy import displacy

import json
import requests
from PIL import Image
import io
import re
from time import time

# Outside Files
import ngram_model as ngm

API_TOKEN = ""  # token in case you want to use private API
headers = {
    # "Authorization": f"Bearer {API_TOKEN}",
    "X-Wait-For-Model": "true",
    "X-Use-Cache": "false"
}
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return Image.open(io.BytesIO(response.content))


def slugify(text):
    # remove non-word characters and foreign characters
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text

def find_haikus(haikus, similar_words):

    training_haikus = []
    for haiku in haikus:
        if any(word in haiku for word in similar_words):
            training_haikus.append(haiku)

    return training_haikus

def train_embeddings(f):
    # Pre-trained GloVe word embeddings
    embeddings_dict = {}
    with open(f, 'r') as f:
        for line in f:
            values = line.split()
            word = values[0]
            vector = np.asarray(values[1:], "float32")
            embeddings_dict[word] = vector

    return embeddings_dict

def read_haikus(f, ngram):
    f = open(f, "r")
    lines = f.readlines()
    haikus = []
    for line in lines:
        haiku = (ngram-1) * "<haiku> "
        haiku += " ".join(line.split(",")[1:4])
        haiku += (ngram-1) * " </haiku>"
        haikus.append(haiku)

    return haikus

def return_haikus(word):

    haikus = read_haikus("all_haiku.csv", 3)
    # embeddings = train_embeddings("glove.6B.100d.txt")
    # print(embeddings["apple"])

    t = find_haikus(haikus, [word])
    #print(len(t))

    ngram_lm = ngm.LanguageModel(2, True, line_begin="<" + "haiku" + ">", line_end="</" + "haiku" + ">")
    # training and testing sets
    train = t

    # training language model
    ngram_lm.train(train)
    #print("trained")

    # print(ngram_lm.generate_sentence(5).split(ngram_lm.line_end)[0].split(ngram_lm.line_begin)[-1])
    #for haiku in ngram_lm.generate_haiku(3):
    #    for line in haiku:
    #        print(line)
    #    print()
    return ngram_lm.generate_haiku(1)

def get_image(prompt):

    #NER = spacy.load("en_core_web_sm")

    #raw_text = "NASA oversaw many people including Donald Trump"
    #text1 = NER(txt)

    #for word in text1.ents:
    #    print("loo")
    #    print(word.text, word.label_)

    image = query({"inputs": prompt})
    #image.save(f"{slugify(prompt)}-{time():.0f}.png")
    image.save("image.png")

    #return f"{slugify(prompt)}-{time():.0f}.png"


def main():

    haikus = read_haikus("all_haiku.csv", 3)
    #embeddings = train_embeddings("glove.6B.100d.txt")
    #print(embeddings["apple"])

    t = find_haikus(haikus, ["love"])
    #print(t[:5])


    ngram_lm = ngm.LanguageModel(2, True, line_begin="<" + "haiku" + ">", line_end="</" + "haiku" + ">")
    # training and testing sets
    train = t

    # training language model
    ngram_lm.train(train)
    #print("trained")

    txt = ''
    #print(ngram_lm.generate_sentence(5).split(ngram_lm.line_end)[0].split(ngram_lm.line_begin)[-1])
    for haiku in ngram_lm.generate_haiku(1):
        for line in haiku:
            print(line)
            txt += line
        print()

    NER = spacy.load("en_core_web_sm")

    raw_text = "NASA oversaw many people including Donald Trump"
    text1 = NER(txt)

    for word in text1.ents:
        print("loo")
        print(word.text, word.label_)

    # generating 25 sentences using trained model
    #generated = ngram_lm.generate(5)
    #print("generated")
    #[print(sentence + "\n") for sentence in generated]



if __name__ == "__main__":
    main()