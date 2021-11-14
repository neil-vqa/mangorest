import pymongo
from flask import Flask, abort, jsonify, request
from flask.wrappers import Response
from flask_cors import CORS

from mangorest import mongo, services

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db = mongo.connect()


@app.get("/api/<collection>")
def get_collection(collection) -> Response:
    try:
        documents = services.fetch_collection(db, collection, request.args)
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


@app.get("/api/<collection>/<oid>")
def get_document(collection, oid) -> Response:
    try:
        document = services.fetch_document(db, collection, oid)
        return jsonify(document)
    except ValueError as e:
        abort(404, description=e)


# TODO: update document
# TODO: delete document
# TODO: collection filtering
