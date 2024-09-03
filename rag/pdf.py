from flask import Blueprint, request, jsonify
import os
import boto3
from dotenv import load_dotenv
import logging
from sentence_transformers import SentenceTransformer
from datetime import date
from botocore.exceptions import NoCredentialsError
import fitz  # PyMuPDF opener
import json
from rag.embed import EmbedChunks
from database.db import collection

load_dotenv()

directory = 'uploads'
os.makedirs(directory, exist_ok=True)

# Load the Sentence Transformer model
model_name = 'distiluse-base-multilingual-cased-v2'

pdf = Blueprint('pdf', __name__)

ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.environ.get("AWS_SECRET_KEY")

S3_BUCKET = os.environ.get("AWS_S3_BUCKET")
S3_REGION = os.environ.get("AWS_S3_REGION")

# create a boto3 session object
session = boto3.Session(
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_KEY,
)
s3 = session.resource('s3')


# Extract text in chunks from PDF
def extract_text_in_chunks(file_path, chunk_size=500):
    doc = fitz.open(file_path)
    text = []
    for page in doc:
        text.append(page.get_text())

    text_str = "".join(text)

    print(len(text))
    chunks = [text_str[i:i+chunk_size]
              for i in range(0, len(text_str), chunk_size)]
    return chunks

# upload pdfs to s3


def upload_file(file_name, bucket, object_name=None):

    if object_name is None:
        object_name = os.path.basename(file_name)

    try:
        s3.meta.client.upload_file(
            Filename=file_name, Bucket=bucket, Key=object_name)
        return True
    except Exception as e:
        logging.error(e)
        return False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'txt'}


@pdf.route("/pdf/process", methods=['POST'])
def process_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # custom_filename = f"{today.year}_{today.day}_{file.filename}"
    file_path = os.path.join(directory, file.filename)
    file.save(file_path)

    # Divide the content in small chunks from   PDF
    text_chunks = extract_text_in_chunks(file_path)

    # initialize the embedding model
    embedder = EmbedChunks(model_name=model_name)

    batch = {"text": text_chunks, "source": file.filename}

    # now generate embeddings
    embeddings_data = embedder(batch)
    embeddings = embeddings_data['embeddings']

    try:
        upload_file(file_path, S3_BUCKET)
        s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"

        # Store embeddings in MongoDB
        for chunk, embedding in zip(text_chunks, embeddings):
            data = {
                "filename": file.filename,
                "document_url": s3_url,
                "embedding": list(embedding),
                "text": chunk,
                "source": file.filename
            }
            print(data)
            collection.insert_one(data)

        return jsonify({'message': 'File uploaded successfully', 's3_url': s3_url}), 200

    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 500
