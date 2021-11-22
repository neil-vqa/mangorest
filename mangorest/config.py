import os
from typing import Dict, List

import pymongo
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.environ["MONGODB_URI"]
DATABASE = os.environ["DATABASE"]
COLLECTION = os.environ["COLLECTIONS"]


class MangoConfigurator:
    def __init__(self, resource_collection_map_list: List[str]) -> None:
        self.resource_collection_map_list = resource_collection_map_list
        self.resource_name_map: Dict[str, str] = {}

    def resource_collection_map_parser(self) -> None:
        """Items in form of resource_name:collection_name"""

        for item in self.resource_collection_map_list:
            resource_name, collection_name = item.split(":")
            self.resource_name_map[resource_name] = collection_name

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
