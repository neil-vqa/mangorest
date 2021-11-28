import os
from typing import Dict, List

import pymongo
from dotenv import load_dotenv

load_dotenv()


MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE = os.environ["DATABASE"]
COLLECTION = os.environ["COLLECTIONS"]
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
MANGO_USER_COLLECTION = os.environ.get("MANGO_USER_COLLECTION", "mangorest_users")


class MangoConfigurator:
    def __init__(self, resource_collection_map_list: List[str]) -> None:
        self.resource_collection_map_list = resource_collection_map_list
        self.resource_name_map: Dict[str, str] = {}

    def resource_collection_map_parser(self) -> None:
        """Build the resource name to collection dict.

        Items are in the form of resource_name:collection_name.
        Resulting dict is in the form of
        {
            "resource_name_1": "collection_name_1",
            "resource_name_2": "collection_name_2",
            ...
        }
        """

        for item in self.resource_collection_map_list:
            resource_name, collection_name = item.split(":")
            self.resource_name_map[resource_name] = collection_name

    def verify_collection_exists(self) -> None:
        client = pymongo.MongoClient(MONGODB_URI)
        database = client[DATABASE]
        collections_list = database.list_collection_names()
        client.close()

        nonexistent_collections: List = []

        for collection in self.resource_name_map.values():
            if collection not in set(collections_list):
                nonexistent_collections.append(collection)

        if nonexistent_collections:
            raise ValueError(
                f"The following collections were not found in {database.name} database.\n"
                "Please check your COLLECTIONS config parameter.\n"
                f"NOT FOUND: {nonexistent_collections}"
            )

    @property
    def collection_set(self):
        return set(self.resource_name_map.values())

    @classmethod
    def from_unmapped_all_collections(cls):
        client = pymongo.MongoClient(MONGODB_URI)
        database = client[DATABASE]
        collections_list = database.list_collection_names()
        client.close()
        resource_collection_list = [f"{item}:{item}" for item in collections_list]
        return cls(resource_collection_list)


LOG_HANDLERS = ["console"]

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} | {module} | {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "DEBUG",
        },
    },
    "loggers": {},
    "root": {"level": "INFO", "handlers": LOG_HANDLERS},
}
