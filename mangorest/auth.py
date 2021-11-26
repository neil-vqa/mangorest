from bson.objectid import ObjectId
from mangorest import config, mongo
import pymongo


def create_user(username: str, password: str) -> ObjectId:
    client = pymongo.MongoClient(config.MONGODB_URI)
    database = client[config.DATABASE]
    users = database["mangorest_users"]

    user_oid = mongo.insert_single_document(
        users, {"username": username, "password": password}
    )
    client.close()

    return user_oid
