from typing import Dict, List, NamedTuple

import pytest

import mangorest.mongo as mongo
import mangorest.services as services
from mangorest import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def db_connection():
    return mongo.connect()


@pytest.fixture
def test_args():
    class TestingArguments(NamedTuple):
        collection_name: str
        query_empty: Dict
        single_doc: Dict
        multiple_doc: List
        updated_doc: Dict
        api_url: str

    doc = {
        "country": "USSR",
        "manufacturer": "NPO Energomash",
        "name": "RD-180",
        "thrust_to_weight_ratio": 90,
    }

    doc_list = [
        {
            "country": "North Pole",
            "manufacturer": "Energomasher",
            "name": "RD-360",
            "thrust_to_weight_ratio": 120,
        },
        {
            "country": "Antarctica",
            "manufacturer": "Energomasher",
            "name": "RD-270",
            "thrust_to_weight_ratio": 110,
        },
    ]

    doc_update = {
        "manufacturer": "Energomasher Inc.",
        "thrust_to_weight_ratio": 150,
    }

    args = TestingArguments("rocketeer", {}, doc, doc_list, doc_update, "/api/rockets")
    return args


@pytest.fixture
def oid_query(db_connection, test_args):
    doc = db_connection[test_args.collection_name].find_one({"name": "RD-180"})
    parsed_doc = services.parse_object_id(doc)

    return parsed_doc["_id"]["$oid"]


# ============================================================
# Testing services
# ============================================================


def test_create_single_document(db_connection, test_args):
    result = services.create_document(
        db_connection, test_args.collection_name, test_args.single_doc
    )
    assert "$oid" in result["_id"]


def test_create_multiple_documents(db_connection, test_args):
    result = services.create_document(
        db_connection, test_args.collection_name, test_args.multiple_doc
    )
    assert len(result) >= 1
    assert "$oid" in result[0]["_id"]


def test_fetch_collection(db_connection, test_args):
    result = services.fetch_collection(
        db_connection,
        test_args.collection_name,
        test_args.query_empty,
        projection=None,
        sort=None,
        limit=1,
        skip=0,
    )
    assert len(result) >= 1


def test_fetch_document(db_connection, test_args, oid_query):
    result = services.fetch_document(
        db_connection, test_args.collection_name, oid_query
    )
    assert "$oid" in result["_id"]


def test_update_document(db_connection, test_args, oid_query):
    result = services.update_document(
        db_connection, test_args.collection_name, oid_query, test_args.updated_doc
    )
    assert result == True


def test_delete_document(db_connection, test_args, oid_query):
    result = services.delete_document(
        db_connection, test_args.collection_name, oid_query
    )
    assert result == True


# ============================================================
# Testing endpoints
# ============================================================


def test_create_document_endpoint(client, test_args):
    resp = client.post(
        test_args.api_url,
        json=test_args.single_doc,
    )
    assert resp.status == "201 CREATED"


def test_get_collection_endpoint(client, test_args):
    resp = client.get(test_args.api_url)
    resp_data = resp.json
    assert isinstance(resp_data, list)


def test_get_document_endpoint(client, test_args, oid_query):
    resp = client.get(f"{ test_args.api_url}/{oid_query}")
    resp_data = resp.json
    oid = resp_data["_id"]["$oid"]
    assert oid_query == oid


def test_update_document_endpoint(client, test_args, oid_query):
    resp = client.patch(f"{ test_args.api_url}/{oid_query}", json=test_args.updated_doc)
    assert resp.status == "204 NO CONTENT"


def test_delete_document_endpoint(client, test_args, oid_query):
    resp = client.delete(f"{test_args.api_url}/{oid_query}")
    assert resp.status == "204 NO CONTENT"
