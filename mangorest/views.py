from typing import Tuple

import bson
from flask import abort, jsonify, request
from flask.wrappers import Response
from flask_cors import CORS
from pymongo.errors import DuplicateKeyError

from mangorest import app, exceptions, mongo, services

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db = mongo.connect()  # The mongodb database configured to be exposed to REST clients


@app.get("/api/<collection>")
def get_collection(collection) -> Response:
    try:
        documents = services.fetch_collection(db, collection, request.args)
        return jsonify(documents)
    except exceptions.CollectionNotFoundError as e:
        abort(404, description=e)


@app.post("/api/<collection>")
def create_document_in_collection(collection) -> Tuple[Response, int]:
    try:
        document = request.json
        document_id = services.create_document(db, collection, document)
        return jsonify(document_id), 201
    except DuplicateKeyError as e:
        abort(400, description=e)
    except exceptions.CollectionNotFoundError as e:
        abort(404, description=e)


@app.get("/api/<collection>/<oid>")
def get_document(collection, oid) -> Response:
    try:
        document = services.fetch_document(db, collection, oid)
        return jsonify(document)
    except exceptions.DocumentNotFoundError as e:
        abort(404, description=e)
    except bson.errors.InvalidId as e:
        abort(400, description=e)
    except exceptions.CollectionNotFoundError as e:
        abort(404, description=e)


@app.put("/api/<collection>/<oid>")
def update_document_in_collection(collection, oid) -> Tuple[Response, int]:
    try:
        document = request.json
        services.update_document(db, collection, oid, document)
        return jsonify(), 204
    except exceptions.DocumentNotFoundError as e:
        abort(404, description=e)
    except bson.errors.InvalidId as e:
        abort(400, description=e)
    except DuplicateKeyError as e:
        abort(400, description=e)
    except exceptions.CollectionNotFoundError as e:
        abort(404, description=e)


@app.delete("/api/<collection>/<oid>")
def delete_document_in_collection(collection, oid) -> Tuple[Response, int]:
    try:
        services.delete_document(db, collection, oid)
        return jsonify(), 204
    except exceptions.DocumentNotFoundError as e:
        abort(404, description=e)
    except bson.errors.InvalidId as e:
        abort(400, description=e)
    except exceptions.CollectionNotFoundError as e:
        abort(404, description=e)


# TODO: endpoint-collection mapping
# TODO: collection filtering
# TODO: jwt auth
# TODO: cli
