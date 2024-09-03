from flask import jsonify
from rag.embed import get_embedding_model
from rag.search import search_documents
from rag.utils import get_client
import time


def response_stream(chat):
    for chunk in chat:
        content = chunk.text
        if content is not None:
            yield content


def prepare_response(chat, stream):
    if stream:
        return response_stream(chat)
    else:
        return chat.text


def send_request(
    llm,
    message,
    max_tokens=None,
    temperature=0.0,
    stream=False,
    max_retries=1,
    retry_interval=60,
):
    retry_count = 0
    client = get_client(llm=llm)
    while retry_count <= max_retries:
        try:
            chat_completion = client.chat(
                model=llm,
                max_tokens=max_tokens,
                temperature=temperature,
                message=message,
            )
             # Access the `text` attribute directly if chat_completion is an object
            if hasattr(chat_completion, 'text'):
                return chat_completion.text
            else:
                raise ValueError("The chat completion object does not have a 'text' attribute.")
        except Exception as e:
            print(f"Exception: {e}")
            time.sleep(retry_interval)  # default is per-minute rate limits
            retry_count += 1
    return "Failed to get response after multiple retries."


def generate_response(
    llm,
    max_tokens=None,
    temperature=0.0,
    system_content="",
    assistant_content="",
    user_content="",
    max_retries=1,
    retry_interval=60,
):
    """Generate response from an LLM."""
    return send_request(
        llm, user_content, max_tokens, temperature, stream=False, max_retries=max_retries, retry_interval=retry_interval
    )


class QueryAgent:
    def __init__(self, embedding_model_name, chunks=None, lexical_index=None, llm="", temperature=0.0, max_context_length=4096, system_content="", assistant_content=""):
        # Embedding Model
        self.embedding_model = get_embedding_model(
            embedding_model_name=embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"device": "cpu", "batch_size": 100},
        )
        self.chunks = chunks

        # LLM
        self.llm = llm
        self.temperature = temperature
        self.context_length = int(0.5 * max_context_length)
        self.max_tokens = int(0.5 * max_context_length)
        self.system_content = system_content
        self.assistant_content = assistant_content

    def __call__(self, query, num_chunks=5, stream=True):
        # Get top relevant context
        context_results = search_documents(
            query=query, embedding_model=self.embedding_model, k=num_chunks
        )

        # If no relevant context is found, handle gracefully
        if not context_results:
            return {
                "question": query,
                "sources": [],
                "document_ids": [],
                "answer": "No relevant context found for the given query.",
                "llm": str(self.llm)  # Ensure llm is serializable
            }

        # Extract document IDs, text chunks, and sources from search results
        document_ids = [str(item["_id"]) for item in context_results]
        context = [item["text"] for item in context_results]
        sources = list(set(item["source"] for item in context_results))

        # Prepare user content for the language model
        user_content = f"query: {query}, context: {context}"

        # Generate a response using the language model
        answer = generate_response(
            llm=self.llm,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system_content=self.system_content,
            assistant_content=self.assistant_content,
            user_content=user_content,
        )

        # Construct the result to return
        result = {
            "question": query,
            "sources": sources,
            "document_ids": document_ids,
            "answer": answer,
            "llm": str(self.llm)  # Ensure llm is serializable
        }

        return result
