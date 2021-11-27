from typing import NamedTuple
from bson.objectid import ObjectId
import pytest

import mangorest.auth as auth
import mangorest.mongo as mongo


@pytest.fixture
def user():
    class TestUser(NamedTuple):
        username: str
        password: str

    dummy = TestUser("neeban", "123qwerty")
    return dummy


@pytest.fixture
def db_connection():
    return mongo.connect()


def test_create_user_service(user):
    resp = auth.create_user_service(user.username, user.password)
    assert type(resp) is ObjectId


def test_login_service(db_connection, user):
    user_collection = db_connection["mangorest_users"]
    resp = auth.login_service(user_collection, user.username, user.password)
    assert type(resp) is auth.MangoUser
