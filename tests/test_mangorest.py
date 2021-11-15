import pytest
from pymongo.database import Database

import mangorest.mongo as mongo
import mangorest.services as services
from mangorest import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_successful_db_connection():
    db = mongo.connect()
    assert isinstance(db, Database)


def test_get_collection_endpoint(client):
    resp = client.get("/api/rocket_engines")
    resp_data = resp.json
    assert isinstance(resp_data, list)


def test_create_document_endpoint(client):
    resp = client.post(
        "/api/rocket_engines",
        json={
            "country": "USSR",
            "manufacturer": "NPO Energomash",
            "name": "RD-180",
            "thrust_to_weight_ratio": 90,
        },
    )
    assert resp.status == "201 CREATED"


def test_get_document_endpoint(client):
    req_oid = "619124108e286c717d5636dd"
    resp = client.get(f"/api/rocket_engines/{req_oid}")
    resp_data = resp.json
    print(resp_data)
    oid = resp_data["_id"]["$oid"]
    assert req_oid == oid


def test_update_document_endpoint(client):
    req_oid = "619124108e286c717d5636dd"
    resp = client.put(
        f"/api/rocket_engines/{req_oid}",
        json={
            "country": "Russia",
            "manufacturer": "NPO Energomash",
            "name": "RD-180",
            "thrust_to_weight_ratio": 90,
        },
    )
    assert resp.status == "204 NO CONTENT"
