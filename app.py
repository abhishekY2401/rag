from flask import Flask, jsonify, request
from flask_cors import CORS
from rag.chat import chat
from rag.pdf import pdf
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    CORS(app, resources={r"/*": {"origins": "*"}},
         supports_credentials=True)  # Enable cors for all routes
    app.config['CORS_HEADERS'] = 'Content-Type'

    app.register_blueprint(chat, url_prefix='/rag')
    app.register_blueprint(pdf, url_prefix='/rag')

    return app


if __name__ == "__main__":
    app = create_app()
    port = os.environ.get('port')
    app.run(host='0.0.0.0', port=port)
