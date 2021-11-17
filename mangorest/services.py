import json
from typing import Any, Dict, List, Optional

from bson import json_util
from bson.objectid import ObjectId
from pymongo.database import Database

from mangorest import config, exceptions, mongo

# collection_set = set(config.COLLECTION.split(","))
resource_to_collection_list = config.COLLECTION.split(",")

mapper = config.MangoConfigurator(resource_to_collection_list)
mapper.resource_collection_map_parser()
endpoints = mapper.resource_name_map
collection_set = mapper.collection_set


def parse_object_id(document):
    """Converts ObjectId to be serializable."""

    if isinstance(document, Dict):
        document["_id"] = json.loads(json_util.dumps(document["_id"]))
        return document
    elif isinstance(document, ObjectId):
        oid = json.loads(json_util.dumps(document))
        oid_dict = {"_id": oid}
        return oid_dict


def check_resource_name(resource_name):
    if not resource_name in endpoints:
        raise ValueError("Invalid API endpoint.")
    return endpoints[resource_name]


def check_collection(collection_name):
    if not collection_name in collection_set:
        raise exceptions.CollectionNotFoundError(
            "Collection not set to be exposed to REST clients."
        )


def fetch_collection(
    db: Database, collection_name: Any, query: Optional[Dict]
) -> List[Dict]:
    """Fetches documents of the specified collection."""

    check_collection(collection_name)
    db_collection = db[collection_name]
    query_result = mongo.query_collection(db_collection, query)
    documents = [parse_object_id(item) for item in query_result]
    return documents


def create_document(db: Database, collection_name: Any, document_obj: Any):
    """Inserts a single or multiple  documents. Returns the objectid."""

    check_collection(collection_name)
    db_collection = db[collection_name]

    if isinstance(document_obj, Dict):
        document_oid = mongo.insert_single_document(db_collection, document_obj)
        return parse_object_id(document_oid)
    elif isinstance(document_obj, List):
        document_oids = mongo.insert_multiple_documents(db_collection, document_obj)
        return [parse_object_id(item) for item in document_oids]


def fetch_document(db: Database, collection_name: Any, oid: str) -> Dict:
    """Fetches the document with the given objectid."""

    check_collection(collection_name)
    db_collection = db[collection_name]
    query_result = mongo.query_document(db_collection, oid)

    if query_result is None:
        raise exceptions.DocumentNotFoundError(
            f"Document with ObjectId {oid} not found."
        )

    parsed_document = parse_object_id(query_result)
    return parsed_document


def update_document(
    db: Database, collection_name: Any, oid: str, document_obj: Any
) -> bool:
    """Updates a single document with the given objectid."""

    check_collection(collection_name)
    db_collection = db[collection_name]
    update_result = mongo.update_single_document(db_collection, oid, document_obj)

    if update_result is None:
        raise exceptions.DocumentNotFoundError(
            f"No UPDATE performed. Document with ObjectId {oid} not found."
        )

    return True


def delete_document(db: Database, collection_name: Any, oid: str) -> bool:
    """Deletes a single document with the given objectid."""

    check_collection(collection_name)
    db_collection = db[collection_name]
    delete_result = mongo.delete_single_document(db_collection, oid)

    if delete_result is None:
        raise exceptions.DocumentNotFoundError(
            f"No DELETE performed. Document with ObjectId {oid} not found."
        )

    return True
