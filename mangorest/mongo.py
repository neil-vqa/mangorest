import logging
from typing import Any, Dict, List, Optional, Tuple

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

logger = logging.getLogger(__name__)


def connect() -> Database:
    try:
        logger.info("Connecting to MongoDB.")
        client = pymongo.MongoClient(config.MONGODB_URI)
        database = client[config.DATABASE]
        logger.info("Connection to MongoDB successful.")
        return database
    except ConfigurationError:
        logger.exception(
            "Incorrectly configured. Please check your MONGODB_URI or DATABASE config."
        )
        raise
    except ConnectionFailure:
        logger.exception("Connecting to MongoDB failed.")
        raise
    except AutoReconnect:
        logger.exception(
            "MongoDB connection lost. Will attempt to reconnect in the next operation."
        )
        raise


def query_collection(
    db_collection: Collection,
    query: Optional[Dict],
    projection: Optional[List],
    sort_options: Optional[List],
    limit: Optional[int],
    skip: Optional[int],
) -> Cursor:
    try:
        result = db_collection.find(
            filter=query,
            projection=projection,
            sort=sort_options,
            limit=limit,
            skip=skip,
        )
        return result
    except Exception:
        logger.exception("An unexpected error happened.")
        raise


def insert_single_document(db_collection: Collection, document_obj: Dict) -> ObjectId:
    try:
        document_obj_id = db_collection.insert_one(document_obj).inserted_id
        return document_obj_id
    except DuplicateKeyError:
        logger.info("Key already exists.")
        raise
    except Exception:
        logger.exception("An unexpected error happened.")
        raise


def insert_multiple_documents(
    db_collection: Collection, document_obj: List
) -> List[ObjectId]:
    try:
        document_obj_ids = db_collection.insert_many(document_obj).inserted_ids
        return document_obj_ids
    except DuplicateKeyError:
        logger.info("Key already exists.")
        raise
    except Exception:
        logger.exception("An unexpected error happened.")
        raise


def query_document(db_collection: Collection, oid: str) -> Dict:
    try:
        document = db_collection.find_one({"_id": ObjectId(oid)})
        return document
    except bson.errors.InvalidId:
        logger.info("Invalid ObjectId.")
        raise
    except Exception:
        logger.exception("An unexpected error happened.")
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
        logger.info("Invalid ObjectId.")
        raise
    except DuplicateKeyError:
        logger.info("Key already exists.")
        raise
    except Exception:
        logger.exception("An unexpected error happened.")
        raise


def update_multiple_documents(
    db_collection: Collection, query: Dict, modifications: Dict
) -> Tuple[int, int]:
    try:
        result = db_collection.update_many(filter=query, update=modifications)
        return (result.matched_count, result.modified_count)
    except Exception:
        logger.exception("An unexpected error happened.")
        raise


def delete_single_document(db_collection: Collection, oid: str) -> Any:
    try:
        result = db_collection.find_one_and_delete({"_id": ObjectId(oid)})
        return result
    except bson.errors.InvalidId:
        logger.info("Invalid ObjectId.")
        raise
    except Exception:
        logger.exception("An unexpected error happened.")
        raise


def delete_multiple_documents(db_collecton: Collection, query: Dict) -> int:
    try:
        result = db_collecton.delete_many(filter=query)
        return result.deleted_count
    except Exception:
        logger.exception("An unexpected error happened.")
        raise
