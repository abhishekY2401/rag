from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer

# Load the Sentence Transformer model
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

# generates numerical representation of text of size 512 x 512
def generate_embeddings(chunks):
    embeddings = [model.encode(chunk) for chunk in chunks]
    return embeddings
