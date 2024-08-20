import numpy as np
from database.db import supabase


def semantic_search(query, embedding_model, k):
    embedding = np.array(embedding_model.embed_query(query))

    response = supabase.rpc('match_documents', {
        'query_embedding': embedding,
        'match_threshold': 0.78,
        'match_count': 10
    }).execute()

    semantic_context = [{"id": row[0], "text": row[1],
                         "source": row[2]} for row in response]

    return semantic_context
