from bson import json_util
from pymongo.database import Database

from mangorest import config

collection_set = set(config.COLLECTION.split(","))


def parse_object_id(document):
    document["_id"] = json_util.dumps(document["_id"])
    return document


def check_collection(collection):
    if not collection in collection_set:
        raise ValueError("Collection not set to be exposed to REST clients.")


def fetch_collection(db: Database, collection):
    check_collection(collection)
    db_collection = db[collection]
    documents = [parse_object_id(item) for item in db_collection.find()]
    return documents


def create_document(db: Database, collection, document_obj):
    check_collection(collection)
    db_collection = db[collection]

    if isinstance(document_obj, dict):
        document_obj_id = db_collection.insert_one(document_obj).inserted_id
        return json_util.dumps(document_obj_id)
    elif isinstance(document_obj, list):
        document_obj_ids = db_collection.insert_many(document_obj).inserted_ids
        return [json_util.dumps(item) for item in document_obj_ids]
