from typing import NamedTuple
from bson.objectid import ObjectId
from mangorest import config, mongo
import nacl.pwhash
import pymongo
from pymongo.collection import Collection


class MangoUser(NamedTuple):
    username: str
    password: bytes


def create_user(users_collection: Collection, username: str, password: str) -> ObjectId:
    password_byte = password.encode("UTF-8")
    hashed_password = nacl.pwhash.str(password_byte)

    oid = mongo.insert_single_document(
        users_collection, {"username": username, "password": hashed_password}
    )
    return oid


def get_user(users_collection: Collection, username: str):
    try:
        print(type(users_collection))
        print(username)
        resp = users_collection.find_one({"username": username})
        if resp:
            user = MangoUser(resp["username"], resp["password"])
            return user
        else:
            return resp
    except Exception:
        raise


def check_password(user, entered_password) -> None:
    correct_user_password = user.password
    entered_user_password = entered_password.encode("UTF-8")

    try:
        nacl.pwhash.verify(correct_user_password, entered_user_password)
    except Exception:
        raise


def create_user_service(username: str, password: str) -> ObjectId:
    """This will mainly be used by the CLI."""

    client = pymongo.MongoClient(config.MONGODB_URI)
    database = client[config.DATABASE]
    users = database["mangorest_users"]

    user_oid = create_user(users, username, password)

    client.close()
    return user_oid


def login_service(user_collection: Collection, username: str, password: str):
    current_user = get_user(user_collection, username)
    if current_user:
        check_password(current_user, password)
        return current_user
    else:
        raise ValueError("User not found.")
