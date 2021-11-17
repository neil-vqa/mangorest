from typing import Any, Dict, List, Optional

import bson
import pymongo
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.errors import (
    AutoReconnect,
    ConfigurationError,
    ConnectionFailure,
    DuplicateKeyError,
)

from mangorest import config


def connect() -> Database:
    try:
        client = pymongo.MongoClient(config.MONGODB_URI)
        database = client[config.DB_SCHEMA]
        return database
    except ConfigurationError:
        raise ConfigurationError(
            "Incorrectly configured. Please check your MONGODB_URI or DB_SCHEMA config."
        )
    except ConnectionFailure:
        raise ConnectionFailure("Connecting to MongoDB failed.")
    except AutoReconnect:
        raise AutoReconnect(
            "MongoDB connection lost. Will attempt to reconnect in the next operation."
        )


def query_collection(db_collection: Collection, query: Optional[Dict]) -> Cursor:
    try:
        result = db_collection.find(query)
        return result
    except Exception:
        raise


def insert_single_document(db_collection: Collection, document_obj: Dict) -> ObjectId:
    try:
        document_obj_id = db_collection.insert_one(document_obj).inserted_id
        return document_obj_id
    except DuplicateKeyError:
        raise
    except Exception:
        raise


def insert_multiple_documents(
    db_collection: Collection, document_obj: List
) -> List[ObjectId]:
    try:
        document_obj_ids = db_collection.insert_many(document_obj).inserted_ids
        return document_obj_ids
    except DuplicateKeyError:
        raise
    except Exception:
        raise


def query_document(db_collection: Collection, oid: str) -> Dict:
    try:
        document = db_collection.find_one({"_id": ObjectId(oid)})
        return document
    except bson.errors.InvalidId:
        raise
    except Exception:
        raise


def update_single_document(
    db_collection: Collection, oid: str, document_obj: Dict
) -> Any:
    try:
        result = db_collection.find_one_and_update(
            {"_id": ObjectId(oid)}, {"$set": document_obj}
        )
        return result
    except bson.errors.InvalidId:
        raise
    except DuplicateKeyError:
        raise
    except Exception:
        raise


def delete_single_document(db_collection: Collection, oid: str) -> Any:
    try:
        result = db_collection.find_one_and_delete({"_id": ObjectId(oid)})
        return result
    except bson.errors.InvalidId:
        raise
    except Exception:
        raise
