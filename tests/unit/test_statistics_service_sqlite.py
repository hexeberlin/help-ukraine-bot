"""Unit tests for StatisticsServiceSQLite."""

from src.infrastructure.sqlite_statistics import StatisticsServiceSQLite


def test_record_request_purges_old_entries():
    service = StatisticsServiceSQLite(retention_seconds=10)

    service.record_request(
        topic="cities",
        topic_description="City chats",
        timestamp=100,
    )
    service.record_request(
        topic="countries",
        topic_description="Country chats",
        timestamp=115,
    )

    cursor = service._conn.execute("SELECT COUNT(*) FROM guidebook_requests")
    count = cursor.fetchone()[0]

    assert count == 1


def test_top_topics():
    service = StatisticsServiceSQLite(retention_seconds=1000)

    service.record_request(
        topic="cities",
        topic_description="City chats",
        timestamp=100,
    )
    service.record_request(
        topic="cities",
        topic_description="City chats",
        timestamp=101,
    )
    service.record_request(
        topic="countries",
        topic_description="Country chats",
        timestamp=102,
    )
    service.record_request(
        topic="cities",
        topic_description="City chats",
        timestamp=103,
    )
    service.record_request(topic="cities", timestamp=104)
    service.record_request(topic="transport", timestamp=105)

    assert service.top_topics(3) == [
        ("City chats", 3),
        ("Country chats", 1),
        ("cities", 1),
    ]
