from rag.embed import get_embedding_model
from rag.search import semantic_search
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
    messages,
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
            chat_completion = client.chat_stream(
                model=llm,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                messages=messages,
            )
            return prepare_response(chat_completion, stream=stream)

        except Exception as e:
            print(f"Exception: {e}")
            time.sleep(retry_interval)  # default is per-minute rate limits
            retry_count += 1
    return ""


def generate_response(
    llm,
    max_tokens=None,
    temperature=0.0,
    stream=False,
    system_content="",
    assistant_content="",
    user_content="",
    max_retries=1,
    retry_interval=60,
):
    """Generate response from an LLM."""
    messages = [
        {"role": role, "content": content}
        for role, content in [
            ("system", system_content),
            ("assistant", assistant_content),
            ("user", user_content),
        ]

        if content
    ]

    return send_request(
        llm, messages, max_tokens, temperature, stream, max_retries, retry_interval
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
        self.context_length = int(
            0.5 * max_context_length
        )
        self.max_tokens = int(
            0.5 * max_context_length
        )
        self.system_content = system_content
        self.assistant_content = assistant_content

    def __call__(self, query, num_chunks=5, stream=True):

        # get top relevant context
        context_results = semantic_search(
            query=query, embedding_model=self.embedding_model, k=num_chunks
        )

        # generate response
        document_ids = [item["id"] for item in context_results]
        context = [item["text"] for item in context_results]
        sources = set([item["source"] for item in context_results])
        user_content = f"query: {query}, context: {context}"
        answer = generate_response(
            llm=self.llm,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=stream,
            system_content=self.system_content,
            assistant_content=self.assistant_content,
            user_content=user_content,
        )

        result = {
            "question": query,
            "sources": sources,
            "document_ids": document_ids,
            "answer": answer,
            "llm": self.llms
        }

        return result
