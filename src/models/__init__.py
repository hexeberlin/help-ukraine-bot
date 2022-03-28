from dataclasses import dataclass
from typing import List
from bson.objectid import ObjectId


@dataclass
class Article:
    _id: ObjectId
    keys: List[str]
    title: str
    content: str

    def __init__(
        self, keys: List[str], title: str, content: str, _id: ObjectId = None
    ) -> None:
        self.keys = keys
        self.title = title
        self.content = content
        self._id = ObjectId() if _id is None else _id

    def __str__(self):
        keys = " ".join(self.keys)
        return f"**keys:** {keys}\n{self.title}\n{self.content}"
