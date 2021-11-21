import datetime
import json
import re
from typing import Any, Dict, List, Optional

import pymongo
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

# TODO: collection limits, pagination, counting
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
    }

    # used for enforcing the type of the list items
    list_variant = {
        "list-int": int,
        "list-float": float,
        "list-str": str,
        "list-date": datetime.date,
        "list-time": datetime.time,
        "list-datetime": datetime.datetime,
        "list-timedelta": datetime.timedelta,
    }

    if query_type in list_variant:
        parsed_query_value = query_value[1:-1].split(",")
        query_value = [list_variant[query_type](item) for item in parsed_query_value]
        return query_value
    return supported_types[query_type](query_value)


def parse_logical_query(query) -> List[Dict]:
    """Parse and convert logical query string to the logical operator form accepted by pymongo.

    Parser for Logical Query Operators, specifically 'and, or, nor' operators.
    Reference: https://docs.mongodb.com/manual/reference/operator/query-logical/

    Args:
        query: A string that contains query expressions joined/disjoined by and/or enclosed with parentheses.

            A single expression is stuctured as field name followed by an operator
            with the field type hint then the value, separated by "." (dots).
            Example: thrust_to_weight_ratio.gt[int].70

            Multiple expressions are separated by commas.
            Example:  "(thrust_to_weight_ratio.gt[int].70,country.eq[str].North Pole,is_active.eq[bool].true)"

    Returns:
        A list of dicts representing as SON objects.
    """

    expressions_list: List[Dict] = []

    logical_pattern = r"^\((.+)\)$"
    expression_pattern = r"^(.+)\.(\w+)\[(.+)\]\.(.+)"

    logical_match = re.search(logical_pattern, query)
    if logical_match:
        raw_expressions_list = logical_match.group(1).split(",")

        for item in raw_expressions_list:
            expression_match = re.search(expression_pattern, item)
            field_name = expression_match.group(1)  # type: ignore
            operator = expression_match.group(2)  # type: ignore
            field_type = expression_match.group(3)  # type: ignore
            field_value = expression_match.group(4)  # type: ignore
            expression_dict = {
                field_name: {f"${operator}": cast_query_types(field_type, field_value)}
            }
            expressions_list.append(expression_dict)

    return expressions_list


def map_to_query_operator(query_params: Dict) -> Dict[Any, Any]:
    """Parse and convert query string to a form accepted by pymongo.

    Args:
        query_params: A dictionary of the parsed query string.

    Returns:
        Dict (representing as SON object) in the form {"field": "value"} or {"field":{"$operator":"value"}}
    """

    filter_dict = {}  # dict representing as SON object

    # Pattern for when matching directly NON-STRING values:
    # After the "=", type hint of the field must be provided.
    # Example: /api/rockets?is_active=[bool].true

    equality_pattern = r"^\[(\w+)\]\.(\w+)"

    # For Comparison Query Operators:
    # Query string must have the operator name with type hint
    # of the field then a "." (dot) to identify the operator.
    # This is then followed by the value.
    # Example: /api/rockets?thrust_to_weight_ratio=lt[int].70
    # Referrence: https://docs.mongodb.com/manual/reference/operator/query-comparison/

    comparison_operator_pattern = r"(^\w+)\[(.+)\]\.(.+)"

    for key, value in query_params.items():
        # regex matching
        equality_match = re.search(equality_pattern, value)
        comparison_match = re.search(comparison_operator_pattern, value)

        if equality_match:
            typed_query_value = cast_query_types(
                query_type=equality_match.group(1), query_value=equality_match.group(2)
            )
            filter_dict[key] = typed_query_value
        elif comparison_match:
            typed_query_value = cast_query_types(
                query_type=comparison_match.group(2),
                query_value=comparison_match.group(3),
            )
            filter_dict[key] = {f"${comparison_match.group(1)}": typed_query_value}
        elif key == "and" or key == "or":
            and_or_expressions_list = parse_logical_query(value)
            logical_operator = f"${key}"
            filter_dict[logical_operator] = and_or_expressions_list
        else:
            filter_dict[key] = value

    return filter_dict


def parse_sort(sort: str) -> Any:
    sort_pairs = sort.split(",")
    sort_list: List = []
    direction_table = {"ascending": pymongo.ASCENDING, "descending": pymongo.DESCENDING}

    pair_pattern = r"^\((.+)\:(.+)\)$"
    for pair in sort_pairs:
        pair_match = re.search(pair_pattern, pair)
        if pair_match:
            pair_tuple = (pair_match.group(1), direction_table[pair_match.group(2)])
            sort_list.append(pair_tuple)

    return sort_list


def fetch_collection(
    db: Database,
    collection_name: Any,
    query: Optional[Dict],
    projection: Optional[str],
    sort: Optional[str],
) -> List[Dict]:
    """Fetches documents of the specified collection."""

    check_collection(collection_name)
    response_fields = projection.split(",") if projection else None
    sort_options = parse_sort(sort) if sort else None
    db_collection = db[collection_name]
    query_result = mongo.query_collection(
        db_collection, query, response_fields, sort_options
    )
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
