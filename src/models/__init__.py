from dataclasses import dataclass
from typing import List
from bson.objectid import ObjectId


@dataclass
class Article:
    _id: ObjectId
    keys: List[str]
    title: str
    content: str
