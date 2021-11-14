import pymongo
from flask import Flask, abort, jsonify, request
from flask.wrappers import Response
from flask_cors import CORS

from mangorest import config, services

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

client = pymongo.MongoClient(config.MONGODB_URI)
db = client[config.DB_SCHEMA]


@app.get("/api/<collection>")
def get_collection(collection) -> Response:
    try:
        documents = services.fetch_collection(db, collection)
        return jsonify(documents)
    except ValueError as e:
        abort(404, description=e)


@app.post("/api/<collection>")
def create_document_in_collection(collection) -> Response:
    try:
        document = request.json
        document_id = services.create_document(db, collection, document)
        return jsonify(document_id)
    except ValueError as e:
        abort(404, description=e)
