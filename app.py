from flask import Flask, jsonify, request
from flask_cors import CORS
from utils.chat import chat
from utils.pdf import pdf

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
CORS(app, resources={r"/*": {"origins": "*"}},
     supports_credentials=True)  # Enable cors for all routes
app.config['CORS_HEADERS'] = 'Content-Type'

app.register_blueprint(chat, url_prefix='/rag')
app.register_blueprint(pdf, url_prefix='/rag')


@app.route('/', methods=['GET'])
def index():
    return "flask server running"


if __name__ == "__main__":
    app.run(debug=True, port=7000)
