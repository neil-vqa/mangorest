import os
from typing import Dict, List

MONGODB_URI = os.environ["MONGODB_URI"]
DB_SCHEMA = os.environ["DB_SCHEMA"]
COLLECTION = os.environ["COLLECTION"]


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
