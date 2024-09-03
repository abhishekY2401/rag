import numpy as np
from database.db import collection


def search_documents(query, embedding_model, k):

    try:
        embeddings = embedding_model.embed_query(query)
        # Perform the vector search
        pipeline = [
            {
                "$vectorSearch": {
                    "queryVector": embeddings,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": k,
                    "index": "default"
                }
            }
        ]

        results = list(collection.aggregate(pipeline))

        return results

    except Exception as e:
        print(f"An error occurred: {e}")
