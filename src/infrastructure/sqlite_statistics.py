"""SQLite-backed statistics service (in-memory)."""

import json
import sqlite3
import threading
import time
from typing import Any, Dict, Optional

from src.domain.protocols import IStatisticsService, StatisticsServiceError


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
                    display_name TEXT,
                    topic TEXT NOT NULL,
                    topic_description TEXT,
                    parameter TEXT,
                    extra_json TEXT,
                    created_at INTEGER NOT NULL
                )
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_requests_created_at ON guidebook_requests(created_at)"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_requests_topic_desc ON guidebook_requests(topic_description)"
            )
            self._conn.commit()

    def record_request(
        self,
        user_id: int,
        topic: str,
        *,
        user_name: Optional[str] = None,
        topic_description: Optional[str] = None,
        parameter: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        created_at = int(time.time()) if timestamp is None else int(timestamp)
        try:
            extra_json = json.dumps(extra) if extra else None
            with self._lock:
                self._conn.execute(
                    """
                    INSERT INTO guidebook_requests (
                        user_id,
                        display_name,
                        topic,
                        topic_description,
                        parameter,
                        extra_json,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        user_name,
                        topic,
                        topic_description,
                        parameter,
                        extra_json,
                        created_at,
                    ),
                )
                cutoff = created_at - self._retention_seconds
                self._conn.execute(
                    "DELETE FROM guidebook_requests WHERE created_at < ?",
                    (cutoff,),
                )
                self._conn.commit()
        except (sqlite3.Error, TypeError, ValueError) as exc:
            raise StatisticsServiceError("Failed to record statistics") from exc

    def top_topics(self, k: int) -> list[tuple[str, int]]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT COALESCE(NULLIF(topic_description, ''), topic) as label, COUNT(*) as cnt
                FROM guidebook_requests
                GROUP BY label
                ORDER BY cnt DESC, label ASC
                LIMIT ?
                """,
                (k,),
            )
            return [(row[0], row[1]) for row in cursor.fetchall()]

    def top_users(self, k: int) -> list[tuple[str, int]]:
        with self._lock:
            cursor = self._conn.execute(
                """
                SELECT display_name, COUNT(*) as cnt
                FROM guidebook_requests
                WHERE display_name IS NOT NULL AND display_name != ''
                GROUP BY display_name
                ORDER BY cnt DESC, display_name ASC
                LIMIT ?
                """,
                (k,),
            )
            return [(row[0], row[1]) for row in cursor.fetchall()]
