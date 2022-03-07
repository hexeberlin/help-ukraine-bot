"""Knowledge base of the bot"""
from uuid import uuid4
import json

from dataclasses import dataclass


@dataclass
class Reply:
    """Reply for an answer"""

    id: str
    title: str
    content: str


replies: list[Reply] = []
with open("knowledge.json", encoding="utf-8") as f:
    records = json.load(f)["replies"]
    replies = [Reply(id=str(uuid4()), **r) for r in records]


def search(query: str) -> list[Reply]:
    """Searches for relevant replies

    Args:
        query (str): query to search for

    Returns:
        list[Reply]: Replies containing query
    """
    result = filter(lambda r: query in r.title or query in r.content, replies)
    return result
