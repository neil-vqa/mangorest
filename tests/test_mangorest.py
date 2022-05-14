from typing import Dict, List, NamedTuple

import pytest

import mangorest.mongo as mongo
import mangorest.services as services
from mangorest import app, exceptions


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
        query_for_updates_deletes: Dict
        multiple_doc_update: Dict
        dummy_oid: str = "61a993c68cd8469da9bd1eb4"

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

    doc_list_update = {"$set": {"country": "Moon"}}

    args = TestingArguments(
        collection_name="rocket_engines",
        query_empty={},
        single_doc=doc,
        multiple_doc=doc_list,
        updated_doc=doc_update,
        api_url="/api/rockets",
        query_for_updates_deletes={"manufacturer": {"$eq": "Energomasher"}},
        multiple_doc_update=doc_list_update,
    )
    return args


@pytest.fixture
def oid_query(db_connection, test_args):
    doc = db_connection[test_args.collection_name].find_one({"name": "RD-180"})
    parsed_doc = services.parse_bson(doc)

    return parsed_doc["_id"]["$oid"]


@pytest.fixture
def user():
    class TestUser(NamedTuple):
        username: str
        password: str

    dummy = TestUser("neeban", "123qwerty")
    return dummy


@pytest.fixture
def jwt_token(client, user):
    resp = client.post(
        "/login",
        json={"username": user.username, "password": user.password},
    )
    return resp.json["access_token"]


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
    assert result is True


def test_delete_document(db_connection, test_args, oid_query):
    result = services.delete_document(
        db_connection, test_args.collection_name, oid_query
    )
    assert result is True


def test_raises_DocumentNotFoundError_when_getting_document(db_connection, test_args):
    with pytest.raises(exceptions.DocumentNotFoundError):
        services.fetch_document(
            db_connection, test_args.collection_name, test_args.dummy_oid
        )


def test_raises_DocumentNotFoundError_when_updating_document(db_connection, test_args):
    with pytest.raises(exceptions.DocumentNotFoundError):
        services.update_document(
            db_connection,
            test_args.collection_name,
            test_args.dummy_oid,
            test_args.updated_doc,
        )


def test_raises_DocumentNotFoundError_when_deleting_document(db_connection, test_args):
    with pytest.raises(exceptions.DocumentNotFoundError):
        services.delete_document(
            db_connection, test_args.collection_name, test_args.dummy_oid
        )


def test_update_many_documents(db_connection, test_args):
    result = services.update_many_documents(
        db_connection,
        test_args.collection_name,
        test_args.query_for_updates_deletes,
        test_args.multiple_doc_update,
    )
    assert type(result) is tuple


def test_raises_EmptyQueryFatalActionError_when_updating_documents_without_query(
    db_connection, test_args
):
    with pytest.raises(exceptions.EmptyQueryFatalActionError):
        services.update_many_documents(
            db_connection,
            test_args.collection_name,
            test_args.query_empty,
            test_args.multiple_doc_update,
        )


def test_delete_many_documents(db_connection, test_args):
    result = services.delete_many_documents(
        db_connection,
        test_args.collection_name,
        test_args.query_for_updates_deletes,
    )
    assert type(result) is int


def test_raises_EmptyQueryFatalActionError_when_deleting_documents_without_query(
    db_connection, test_args
):
    with pytest.raises(exceptions.EmptyQueryFatalActionError):
        services.delete_many_documents(
            db_connection,
            test_args.collection_name,
            test_args.query_empty,
        )


# ============================================================
# Testing endpoints
# ============================================================


def test_login_endpoint(user, client):
    resp = client.post(
        "/login",
        json={"username": user.username, "password": user.password},
    )
    assert "access_token" in resp.json


def test_create_document_endpoint(client, test_args, jwt_token):
    resp = client.post(
        test_args.api_url,
        json=test_args.single_doc,
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert resp.status == "201 CREATED"


def test_create_many_documents_endpoint(client, test_args, jwt_token):
    resp = client.post(
        test_args.api_url,
        json=test_args.multiple_doc,
        headers={"Authorization": f"Bearer {jwt_token}"},
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


def test_update_document_endpoint(client, test_args, oid_query, jwt_token):
    resp = client.patch(
        f"{ test_args.api_url}/{oid_query}",
        json=test_args.updated_doc,
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert resp.status == "204 NO CONTENT"


def test_update_many_documents_endpoint(client, test_args, jwt_token):
    resp = client.patch(
        f"{test_args.api_url}?manufacturer=Energomasher",
        json=test_args.multiple_doc_update,
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert resp.json["matched_items"] == 2
    assert resp.json["modified_items"] == 2
    assert resp.status == "200 OK"


def test_delete_document_endpoint(client, test_args, oid_query, jwt_token):
    resp = client.delete(
        f"{test_args.api_url}/{oid_query}",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert resp.status == "204 NO CONTENT"


def test_delete_many_documents_endpoint(client, test_args, jwt_token):
    resp = client.delete(
        f"{test_args.api_url}?manufacturer=Energomasher",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert resp.json["items_deleted"] == 2
    assert resp.status == "200 OK"


def test_response_forbidden_when_updating_documents_without_query(
    client, test_args, jwt_token
):
    resp = client.patch(
        test_args.api_url,
        json=test_args.multiple_doc_update,
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert resp.status == "403 FORBIDDEN"


def test_response_forbidden_when_deleting_documents_without_query(
    client, test_args, jwt_token
):
    resp = client.delete(
        test_args.api_url,
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert resp.status == "403 FORBIDDEN"
