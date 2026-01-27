"""Unit tests for StatisticsServiceSQLite."""

from src.infrastructure.sqlite_statistics import StatisticsServiceSQLite


def test_record_request_purges_old_entries():
    service = StatisticsServiceSQLite(retention_seconds=10)

    service.record_request(user_id=1, topic="cities", timestamp=100)
    service.record_request(user_id=2, topic="countries", timestamp=115)

    cursor = service._conn.execute(  # type: ignore[attr-defined]
        "SELECT COUNT(*) FROM guidebook_requests"
    )
    count = cursor.fetchone()[0]

    assert count == 1


def test_top_topics_and_users():
    service = StatisticsServiceSQLite(retention_seconds=1000)

    service.record_request(user_id=1, topic="cities", timestamp=100)
    service.record_request(user_id=2, topic="cities", timestamp=101)
    service.record_request(user_id=1, topic="countries", timestamp=102)
    service.record_request(user_id=1, topic="cities", timestamp=103)

    assert service.top_topics(2) == [("cities", 3), ("countries", 1)]
    assert service.top_users(2) == [(1, 3), (2, 1)]
