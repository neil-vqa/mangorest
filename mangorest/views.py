from typing import Tuple

import bson
import flask_cors
import flask_jwt_extended as flask_jwt
import nacl.exceptions
from flask import abort, jsonify, request
from flask.wrappers import Response

from mangorest import app, auth, config, exceptions, mongo, services

jwt_auth = flask_jwt.JWTManager(app)
cors_init = flask_cors.CORS(app, resources={r"/api/*": {"origins": "*"}})
db = mongo.connect()  # The mongodb database configured to be exposed to REST clients

# ===============================================
# error handlers for serializing error messages
# ===============================================


@app.errorhandler(400)
def bad_request(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(401)
def unathorized_request(e):
    return jsonify(error=str(e)), 401


@app.errorhandler(403)
def forbidden_action(e):
    return jsonify(error=str(e)), 403


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


# ===============================================
# endpoints
# ===============================================


@app.get("/api/<resource>")
def get_collection(resource) -> Response:
    try:
        collection_name = services.check_resource_name(resource)
        request_args = request.args.copy()

        projection = request_args.pop(
            "_projection", None
        )  # eg. _projection=name,thrust_to_weight_ratio

        sort = request_args.pop(
            "_sort", None
        )  # eg. _sort=(name:ascending),(thrust_to_weight_ratio:descending)

        limit = request_args.pop("_limit", None)  # eg. _limit=23
        skip = request_args.pop("_skip", None)  # eg. _skip=10

        query = services.map_to_query_operator(request_args)
        documents = services.fetch_collection(
            db, collection_name, query, projection, sort, limit, skip
        )
        return jsonify(documents)
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)


@app.post("/api/<resource>")
@flask_jwt.jwt_required()
def create_document_in_collection(resource) -> Tuple[Response, int]:
    """Endpoint for creating single or multiple documents."""

    try:
        collection_name = services.check_resource_name(resource)
        document = request.json
        document_id = services.create_document(db, collection_name, document)
        return jsonify(document_id), 201
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)


@app.patch("/api/<resource>")
@flask_jwt.jwt_required()
def update_documents_in_collection(resource) -> Tuple[Response, int]:
    """Endpoint for  updating multiple documents."""

    try:
        collection_name = services.check_resource_name(resource)
        request_args = request.args.copy()
        filters = ["_projection", "_sort", "_limit", "_skip"]

        for item in filters:
            request_args.pop(item, None)

        modifications = request.json
        query = services.map_to_query_operator(request_args)
        matched_items, modified_items = services.update_many_documents(
            db, collection_name, query, modifications  # type: ignore
        )
        return jsonify(matched_items=matched_items, modified_items=modified_items), 200
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)
    except exceptions.EmptyQueryFatalActionError as e:
        abort(403, description=e)


@app.delete("/api/<resource>")
@flask_jwt.jwt_required()
def delete_documents_in_collection(resource) -> Tuple[Response, int]:
    """Endpoint for deleting multiple documents."""

    try:
        collection_name = services.check_resource_name(resource)
        request_args = request.args.copy()
        filters = ["_projection", "_sort", "_limit", "_skip"]

        for item in filters:
            request_args.pop(item, None)

        query = services.map_to_query_operator(request_args)
        items_deleted = services.delete_many_documents(
            db, collection_name, query  # type: ignore
        )
        return jsonify(items_deleted=items_deleted), 200
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)
    except exceptions.EmptyQueryFatalActionError as e:
        abort(403, description=e)


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


@app.patch("/api/<resource>/<oid>")
@flask_jwt.jwt_required()
def update_document_in_collection(resource, oid) -> Tuple[Response, int]:
    try:
        collection_name = services.check_resource_name(resource)
        document = request.json
        services.update_document(db, collection_name, oid, document)
        return jsonify(), 204
    except exceptions.ResourceNameNotFoundError as e:
        abort(404, description=e)
    except exceptions.DocumentNotFoundError as e:
        abort(404, description=e)
    except bson.errors.InvalidId as e:
        abort(400, description=e)


@app.delete("/api/<resource>/<oid>")
@flask_jwt.jwt_required()
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


# authentication-related


@jwt_auth.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user = auth.get_user(db[config.MANGO_USER_COLLECTION], identity)
    return user


@app.post("/login")
def login() -> Response:
    try:
        username = request.json.get("username", None)  # type: ignore
        password = request.json.get("password", None)  # type: ignore

        verified_user = auth.login_service(
            db[config.MANGO_USER_COLLECTION], username, password
        )
        access_token = flask_jwt.create_access_token(identity=verified_user.username)
        return jsonify(access_token=access_token)
    except (AttributeError, ValueError, nacl.exceptions.InvalidkeyError):
        abort(401, description="Bad username or password")


@app.get("/me")
@flask_jwt.jwt_required()
def current_user_endpoint():
    return jsonify(username=flask_jwt.current_user.username)
