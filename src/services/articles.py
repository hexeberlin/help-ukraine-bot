import logging
from typing import List
from pymongo.database import Database, Collection
from models import Article
from dataclasses import asdict


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class DuplicateKeyError(Exception):
    pass


class Articles:
    collection: Collection

    def __init__(self, db: Database, collection_name: str) -> None:
        self.collection = db.get_collection(collection_name)

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
            # for item in cursor:
            #     logger.info(item)
            #     logger.info(Article(**item))
            articles = [Article(**item) for item in cursor]
            return articles
