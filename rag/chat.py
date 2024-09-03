from database.db import collection
from flask import Blueprint, request, jsonify
from rag.agent.query import QueryAgent

chat = Blueprint('chat', __name__)


@chat.route('/chat', methods=['POST'])
def chatWithLLM():
    data = request.json
    messages = data.get("messages", [])

    if len(messages) == 1:
        query = messages[0].get("content", '')
        print(query)
        # instantiate the query agent
        agent = QueryAgent(
            embedding_model_name='distiluse-base-multilingual-cased-v2',
            chunks=30,
            llm="command-r"
        )
        result = agent(
            query=query,
            num_chunks=30,
            stream=True,
        )
        print(result)
        return jsonify(result)

    else:
        return jsonify({"error": "Multi-message input not implemented"}), 400
