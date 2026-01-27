"""SQLite-backed statistics service (in-memory)."""

import json
import sqlite3
import threading
import time
from typing import Any, Dict, Optional

from src.domain.protocols import IStatisticsService


class StatisticsServiceSQLite(IStatisticsService):
    """Record guidebook requests in an in-memory SQLite database."""

    def __init__(self, *, retention_seconds: int = 30 * 24 * 60 * 60) -> None:
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._lock = threading.Lock()
        self._retention_seconds = retention_seconds
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guidebook_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    parameter TEXT,
                    extra_json TEXT,
                    created_at INTEGER NOT NULL
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_requests_created_at ON guidebook_requests(created_at)"
            )
            self._conn.commit()

    def record_request(
        self,
        user_id: int,
        topic: str,
        *,
        parameter: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        created_at = int(time.time()) if timestamp is None else int(timestamp)
        extra_json = json.dumps(extra) if extra else None
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO guidebook_requests (user_id, topic, parameter, extra_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, topic, parameter, extra_json, created_at),
            )
            cutoff = created_at - self._retention_seconds
            self._conn.execute(
                "DELETE FROM guidebook_requests WHERE created_at < ?",
                (cutoff,),
            )
            self._conn.commit()

    def top_topics(self, k: int) -> list[tuple[str, int]]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT topic, COUNT(*) as cnt
                FROM guidebook_requests
                GROUP BY topic
                ORDER BY cnt DESC, topic ASC
                LIMIT ?
                """,
                (k,),
            )
            return [(row[0], row[1]) for row in cursor.fetchall()]

    def top_users(self, k: int) -> list[tuple[int, int]]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT user_id, COUNT(*) as cnt
                FROM guidebook_requests
                GROUP BY user_id
                ORDER BY cnt DESC, user_id ASC
                LIMIT ?
                """,
                (k,),
            )
            return [(row[0], row[1]) for row in cursor.fetchall()]
