"""Knowledge base of the bot"""
from typing import List
from uuid import uuid4
import json


class Reply:
    """Reply for an answer"""

    id: str
    title: str
    lower_title: str
    content: str
    lower_content: str

    def __init__(self, title: str, content: str) -> None:
        self.id = str(uuid4())
        self.title = title
        self.lower_title = title.lower()
        self.content = content
        self.lower_content = content.lower()


replies: List[Reply] = []
with open("knowledge.json", encoding="utf-8") as f:
    records = json.load(f)["replies"]
    replies = [Reply(**r) for r in records]


def search(query: str) -> List[Reply]:
    """Searches for relevant replies

    Args:
        query (str): query to search for

    Returns:
        list[Reply]: Replies containing query
    """
    lower_query = query.lower()
    result = filter(
        lambda r: lower_query in r.lower_title or query in r.lower_content, replies
    )
    return result
