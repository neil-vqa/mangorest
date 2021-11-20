import datetime
import json
import re
from typing import Any, Dict, List, Optional

from bson import json_util
from bson.objectid import ObjectId
from pymongo.database import Database

from mangorest import config, exceptions, mongo

if config.COLLECTION == "*":
    mapper = config.MangoConfigurator.from_unmapped_all_collections()
else:
    resource_to_collection_list = config.COLLECTION.split(",")
    mapper = config.MangoConfigurator(resource_to_collection_list)

mapper.resource_collection_map_parser()
endpoints = mapper.resource_name_map
collection_set = mapper.collection_set

# TODO: collection filtering, projection
# TODO: collection ordering, limits, pagination, counting
# TODO: custom functions for complex collection filtering
# TODO: logging
# TODO: jwt auth
# TODO: cli (user creation)


def parse_object_id(document):
    """Converts ObjectId to be serializable."""

    if type(document) is dict:
        document["_id"] = json.loads(json_util.dumps(document["_id"]))
        return document
    elif type(document) is ObjectId:
        oid = json.loads(json_util.dumps(document))
        oid_dict = {"_id": oid}
        return oid_dict


def check_resource_name(resource_name):
    if not resource_name in endpoints:
        raise exceptions.ResourceNameNotFoundError("API endpoint does not exist.")
    return endpoints[resource_name]


def check_collection(collection_name):
    if not collection_name in collection_set:
        raise exceptions.CollectionNotFoundError(
            "Collection not set to be exposed to REST clients."
        )


def cast_query_types(query_type, query_value) -> Any:
    supported_types = {
        "int": int,
        "float": float,
        "bool": bool,
        "str": str,
        "date": datetime.date,
        "time": datetime.time,
        "datetime": datetime.datetime,
        "timedelta": datetime.timedelta,
        "list": list,
    }

    return supported_types[query_type](query_value)


def map_to_query_operator(query_params: Dict) -> Dict:
    """Parse and convert query string to a form accepted by pymongo.

    Return in the form {"field": "value"} or {"field":{"$operator":"value"}}
    """

    # For Comparison Query Operators:
    # Query string must escape "\$" followed by operator name with type info
    # of the field then a "." (dot) to identify the operator.
    # Example: /api/rockets?thrust_to_weight_ratio=\$lt[int].70
    # Referrence: (https://docs.mongodb.com/manual/reference/operator/query-comparison/)

    operator_pattern = r"(^\$\w+)\[(\w+)\]\.(\w+)"
    filter_dict = {}

    for key, value in query_params.items():
        match = re.search(operator_pattern, value)
        if match:
            typed_query_value = cast_query_types(match.group(2), match.group(3))
            filter_dict[key] = {match.group(1): typed_query_value}
        else:
            filter_dict[key] = value

    return filter_dict


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

    if type(document_obj) is dict:
        document_oid = mongo.insert_single_document(db_collection, document_obj)
        return parse_object_id(document_oid)
    elif type(document_obj) is list:
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
