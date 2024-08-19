from database.db import supabase
from flask import Blueprint, request, jsonify

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
