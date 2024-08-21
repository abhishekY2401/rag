from database.db import supabase
from flask import Blueprint, request, jsonify
from rag.agent.query import QueryAgent

chat = Blueprint('chat', __name__)


@chat.route('/chat/create', methods=['POST'])
def createChat():
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')

        print(title, " ", description)

        # create table and insert values
        data, count = supabase.table('chat').insert({
            "title": title,
            "description": description
        }).execute()

        response = {
            "msg": "succesfully created a chat",
            "data": data[1][0]
        }

        return response
    except Exception as e:
        return jsonify({"msg": str(e)}), 500


@chat.route('/chat', methods=['POST'])
def chatWithLLM():
    data = request.json
    messages = data.get("messages", [])

    if len(messages) == 1:
        query = messages[0].get("content", '')
        # instantiate the query agent
        agent = QueryAgent(
            embedding_model_name="embed-english-v3.0",
            chunks=30,
            llm="command-r"
        )
        result = agent(
            query=query,
            num_chunks=30,
            stream=False,
        )
        return jsonify(result)

    else:
        return jsonify({"error": "Multi-message input not implemented"}), 400
