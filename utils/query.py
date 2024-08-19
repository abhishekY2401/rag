from embeddings import generate_embeddings
from database.db import supabase


def perform_semantic_search(query):
    query_vec = generate_embeddings(query)
    query_vec_str = ','.join(map(str, query_vec))

    response = supabase.rpc(
        'match_documents', {'query_embedding': query_vec_str, 'match_threshold': 0.8}).execute()

    return response.data


# user query
user_query = "Can you explain what is Gnapika?"
search_results = perform_semantic_search(user_query)

# Print retrieved documents
for result in search_results:
    print(result['document_text'])
