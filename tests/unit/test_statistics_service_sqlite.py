"""Unit tests for StatisticsServiceSQLite."""

import pytest

from src.domain.protocols import StatisticsServiceError
from src.infrastructure.sqlite_statistics import StatisticsServiceSQLite


def test_record_request_purges_old_entries():
    service = StatisticsServiceSQLite(retention_seconds=10)

    service.record_request(
        user_id=1,
        user_name="User One",
        topic="cities",
        topic_description="City chats",
        timestamp=100,
    )
    service.record_request(
        user_id=2,
        user_name="User Two",
        topic="countries",
        topic_description="Country chats",
        timestamp=115,
    )

    cursor = service._conn.execute("SELECT COUNT(*) FROM guidebook_requests")
    count = cursor.fetchone()[0]

    assert count == 1


def test_top_topics_and_users():
    service = StatisticsServiceSQLite(retention_seconds=1000)

    service.record_request(
        user_id=1,
        user_name="Alice Smith",
        topic="cities",
        topic_description="City chats",
        timestamp=100,
    )
    service.record_request(
        user_id=2,
        user_name="Bob Jones",
        topic="cities",
        topic_description="City chats",
        timestamp=101,
    )
    service.record_request(
        user_id=1,
        user_name="Alice Smith",
        topic="countries",
        topic_description="Country chats",
        timestamp=102,
    )
    service.record_request(
        user_id=1,
        user_name="Alice Smith",
        topic="cities",
        topic_description="City chats",
        timestamp=103,
    )
    service.record_request(user_id=3, topic="cities", timestamp=104)
    service.record_request(user_id=4, topic="transport", timestamp=105)

    assert service.top_topics(3) == [
        ("City chats", 3),
        ("Country chats", 1),
        ("cities", 1),
    ]
    assert service.top_users(2) == [("Alice Smith", 3), ("Bob Jones", 1)]


def test_record_request_raises_statistics_service_error_on_bad_extra():
    service = StatisticsServiceSQLite(retention_seconds=1000)

    with pytest.raises(StatisticsServiceError):
        service.record_request(
            user_id=1,
            user_name="Bad Extra",
            topic="cities",
            topic_description="City chats",
            extra={"bad": object()},
            timestamp=100,
        )
