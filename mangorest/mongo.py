from typing import Dict, List, Optional

import pymongo
from bson.objectid import ObjectId
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.errors import AutoReconnect, ConnectionFailure

from mangorest import config


def connect() -> Database:
    try:
        client = pymongo.MongoClient(config.MONGODB_URI)
        database = client[config.DB_SCHEMA]
        return database
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
    except Exception:
        raise


def insert_multiple_documents(
    db_collection: Collection, document_obj: List
) -> List[ObjectId]:
    try:
        document_obj_ids = db_collection.insert_many(document_obj).inserted_ids
        return document_obj_ids
    except Exception:
        raise


def query_document(db_collection: Collection, oid: str) -> Dict:
    try:
        document = db_collection.find_one({"_id": ObjectId(oid)})
        return document
    except Exception:
        raise


def update_single_document(
    db_collection: Collection, oid: str, document_obj: Dict
) -> bool:
    try:
        db_collection.update_one({"_id": ObjectId(oid)}, {"$set": document_obj})
        return True
    except Exception:
        raise


def delete_single_document(db_collection: Collection, oid: str) -> bool:
    try:
        db_collection.delete_one({"_id": ObjectId(oid)})
        return True
    except Exception:
        raise
