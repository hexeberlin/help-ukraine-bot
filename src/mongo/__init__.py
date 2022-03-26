import logging
from pymongo import MongoClient
from pymongo.database import Database

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def connect(host: str, user: str, password: str, database: str) -> Database:
    connection_string = (
        f"mongodb+srv://{user}:{password}@{host}/?retryWrites=true&w=majority"
    )

    client = MongoClient(connection_string)
    return client.get_database(database)
