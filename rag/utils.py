import cohere
import openai
import os


def get_client(llm):
    if llm.startswith("gpt"):
        base_url = os.environ["OPENAI_API_BASE"]
        api_key = os.environ["OPENAI_API_KEY"]
        client = openai.OpenAI(base_url=base_url, api_key=api_key)
    else:
        # For Cohere
        api_key = os.environ["COHERE_API_KEY"]
        client = cohere.Client(api_key)
    return client
