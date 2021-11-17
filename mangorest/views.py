from typing import Tuple

import bson
from flask import abort, jsonify, request
from flask.wrappers import Response
from flask_cors import CORS
from pymongo.errors import DuplicateKeyError

from mangorest import app, exceptions, mongo, services

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

db = mongo.connect()  # The mongodb database configured to be exposed to REST clients


@app.get("/api/<resource>")
def get_collection(resource) -> Response:
    try:
        collection_name = services.check_resource_name(resource)
        documents = services.fetch_collection(db, collection_name, request.args)
        return jsonify(documents)
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)
    except exceptions.CollectionNotFoundError as e:
        abort(404, description=e)


@app.post("/api/<resource>")
def create_document_in_collection(resource) -> Tuple[Response, int]:
    try:
        document = request.json
        collection_name = services.check_resource_name(resource)
        document_id = services.create_document(db, collection_name, document)
        return jsonify(document_id), 201
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)
    except DuplicateKeyError as e:
        abort(400, description=e)
    except exceptions.CollectionNotFoundError as e:
        abort(404, description=e)


@app.get("/api/<resource>/<oid>")
def get_document(resource, oid) -> Response:
    try:
        collection_name = services.check_resource_name(resource)
        document = services.fetch_document(db, collection_name, oid)
        return jsonify(document)
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)
    except exceptions.DocumentNotFoundError as e:
        abort(404, description=e)
    except bson.errors.InvalidId as e:
        abort(400, description=e)
    except exceptions.CollectionNotFoundError as e:
        abort(404, description=e)


@app.put("/api/<resource>/<oid>")
def update_document_in_collection(resource, oid) -> Tuple[Response, int]:
    try:
        document = request.json
        collection_name = services.check_resource_name(resource)
        services.update_document(db, collection_name, oid, document)
        return jsonify(), 204
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)
    except exceptions.DocumentNotFoundError as e:
        abort(404, description=e)
    except bson.errors.InvalidId as e:
        abort(400, description=e)
    except DuplicateKeyError as e:
        abort(400, description=e)
    except exceptions.CollectionNotFoundError as e:
        abort(404, description=e)


@app.delete("/api/<resource>/<oid>")
def delete_document_in_collection(resource, oid) -> Tuple[Response, int]:
    try:
        collection_name = services.check_resource_name(resource)
        services.delete_document(db, collection_name, oid)
        return jsonify(), 204
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)
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
