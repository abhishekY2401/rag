import os
from langchain_cohere import CohereEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

# Load the Sentence Transformer model
# model = SentenceTransformer('distiluse-base-multilingual-cased-v2')


def get_embedding_model(embedding_model_name, model_kwargs, encode_kwargs):
    if embedding_model_name == "embed-english-v3.0":
        embedding_model = CohereEmbeddings(
            model=embedding_model_name,
        )
    else:
        embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

    return embedding_model


class EmbedChunks:
    def __init__(self, model_name):
        # Embedding Model
        self.embedding_model = get_embedding_model(
            embedding_model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"device": "cpu", "batch_size": 500}
        )

    def __call__(self, batch):
        embeddings = self.embedding_model.embed_documents(batch["text"])
        return {"text": batch["text"], "source": batch["source"], "embeddings": embeddings}
