import logging
import re
from typing import List
from pymongo.database import Database, Collection
from src.models import Article
from dataclasses import asdict


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class DuplicateKeyError(Exception):
    pass


class Articles:
    collection: Collection
    find_limit: 5

    def __init__(self, db: Database, collection_name: str) -> None:
        self.collection = db.get_collection(collection_name)
        self.find_limit = 5

    def __validate_keys(self, keys: List[str]) -> bool:
        # TODO: Check uniqueness
        return len(keys) > 0

    def add(self, article: Article) -> None:
        if self.__validate_keys(article.keys):
            document = asdict(article)
            self.collection.insert_one(document)
        else:
            raise DuplicateKeyError()

    def list(self) -> List[Article]:
        with self.collection.find() as cursor:
            articles = [Article(**item) for item in cursor]
            return articles

    def get(self, key: str) -> Article:
        document = self.collection.find_one({"keys": key})
        return Article(**document)

    def delete(self, key: str) -> Article:
        self.collection.find_one_and_delete({"keys": key})

    def find(self, text: str) -> List[Article]:
        regx = re.compile(f"/.*{text}.*/", re.IGNORECASE)
        with self.collection.find({"keys": text, "title": regx, "content": regx}).limit(
            self.find_limit
        ) as articles:
            return list(articles)
