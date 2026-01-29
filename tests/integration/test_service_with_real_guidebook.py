"""Integration tests using real YamlGuidebook with actual YAML files."""

import pytest
from src.infrastructure.yaml_guidebook import YamlGuidebook
from src.application.berlin_help_service import BerlinHelpService


@pytest.fixture
def real_guidebook():
    """Create a real YamlGuidebook instance."""
    return YamlGuidebook(
        guidebook_path="src/knowledgebase/guidebook.yml",
        vocabulary_path="src/knowledgebase/vocabulary.yml"
    )


@pytest.fixture
def service(real_guidebook):
    """Create a BerlinHelpService with real guidebook."""
    return BerlinHelpService(guidebook=real_guidebook)


class TestServiceWithRealGuidebook:
    """Integration tests with real guidebook data."""

    def test_handle_help_returns_formatted_text(self, service):
        """Test that handle_help returns properly formatted help text."""
        result = service.handle_help()

        # Should contain the separator
        assert "=" in result
        # Should contain multilingual content
        assert "Привет" in result
        assert "Вітання" in result
        assert "Hi!" in result

    def test_handle_topic_with_real_topic(self, service, real_guidebook):
        """Test handle_topic with a real topic from the guidebook."""
        topics = real_guidebook.get_topics()
        if topics:
            topic = topics[0]
            result = service.handle_topic(topic)

            # Should have hashtag
            assert result.startswith(f"#{topic}\n")
            # Should have content
            assert len(result) > len(f"#{topic}\n")

    def test_handle_cities_with_berlin(self, service):
        """Test handle_cities with Berlin."""
        result = service.handle_cities("Berlin", show_all=False)

        # Should return city information, not error
        assert "Berlin" in result or "berlin" in result
        # Should have formatting
        assert "=" in result

    def test_handle_cities_without_name(self, service):
        """Test handle_cities without city name shows prompt."""
        result = service.handle_cities(None, show_all=False)

        # Should ask for city name
        assert "город" in result.lower() or "city" in result.lower()

    def test_handle_cities_show_all(self, service):
        """Test handle_cities with show_all flag."""
        result = service.handle_cities(None, show_all=True)

        # Should show multiple cities
        assert len(result) > 50  # Reasonable assumption for formatted city list

    def test_handle_countries_with_poland(self, service):
        """Test handle_countries with Poland."""
        result = service.handle_countries("Poland", show_all=False)

        # Should return country information
        assert isinstance(result, str)
        assert len(result) > 0

    def test_handle_countries_without_name(self, service):
        """Test handle_countries without country name shows prompt."""
        result = service.handle_countries(None, show_all=False)

        # Should ask for country name
        assert "стран" in result.lower() or "country" in result.lower()

    def test_handle_countries_show_all(self, service):
        """Test handle_countries with show_all flag."""
        result = service.handle_countries(None, show_all=True)

        # Should show multiple countries
        assert isinstance(result, str)
        assert len(result) > 0

    def test_all_topics_can_be_handled(self, service, real_guidebook):
        """Test that all topics in the guidebook can be handled."""
        topics = real_guidebook.get_topics()

        for topic in topics:
            # Skip special topics that need parameters
            if topic in {"cities", "countries"}:
                continue

            result = service.handle_topic(topic)

            # Should have hashtag and content
            assert result.startswith(f"#{topic}\n")
            assert len(result) > len(f"#{topic}\n")
            # Should not be an error message
            assert "не располагаем информацией" not in result
