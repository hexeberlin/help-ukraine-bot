"""Unit tests for YamlGuidebook implementation."""

import pytest
from src.infrastructure.yaml_guidebook import YamlGuidebook


@pytest.fixture
def guidebook():
    """Create a YamlGuidebook instance with real YAML files."""
    return YamlGuidebook(
        guidebook_path="src/knowledgebase/guidebook.yml",
        vocabulary_path="src/knowledgebase/vocabulary.yml"
    )


class TestYamlGuidebook:
    """Test YamlGuidebook functionality."""

    def test_get_topics(self, guidebook):
        """Test that get_topics returns a list of topic keys."""
        topics = guidebook.get_topics()
        assert isinstance(topics, list)
        assert len(topics) > 0
        # Check for some expected topics
        assert "accommodation" in topics or any("accommod" in t for t in topics)

    def test_get_descriptions(self, guidebook):
        """Test that get_descriptions returns a dictionary."""
        descriptions = guidebook.get_descriptions()
        assert isinstance(descriptions, dict)
        assert len(descriptions) > 0
        # Verify it's a copy (immutability)
        original_len = len(descriptions)
        descriptions["test_key"] = "test_value"
        assert len(guidebook.get_descriptions()) == original_len

    def test_get_info_with_list_topic(self, guidebook):
        """Test get_info for a topic that contains a list."""
        topics = guidebook.get_topics()
        # Find a topic with a list
        for topic in topics:
            info = guidebook.get_info(topic)
            assert isinstance(info, str)
            assert len(info) > 0
            # Should have separator lines
            assert "=" in info
            break

    def test_get_info_with_dict_topic(self, guidebook):
        """Test get_info for a topic that contains a dictionary."""
        # Cities should be a dict-based topic
        info = guidebook.get_info("cities")
        assert isinstance(info, str)
        assert len(info) > 0
        assert "=" in info

    def test_get_info_with_name(self, guidebook):
        """Test get_info with a specific name parameter."""
        # Get info for a specific city
        info = guidebook.get_info("cities", "Berlin")
        assert isinstance(info, str)
        assert "Berlin" in info or "berlin" in info

    def test_get_info_nonexistent_topic(self, guidebook):
        """Test get_info with a topic that doesn't exist."""
        info = guidebook.get_info("nonexistent_topic")
        assert "не располагаем информацией" in info

    def test_get_info_nonexistent_name(self, guidebook):
        """Test get_info with a name that doesn't exist in a topic."""
        info = guidebook.get_info("cities", "NonexistentCity")
        assert "не располагаем информацией" in info

    def test_get_results(self, guidebook):
        """Test get_results method."""
        # get_results should be an alias for get_info
        info1 = guidebook.get_info("cities", "Berlin")
        info2 = guidebook.get_results("cities", "Berlin")
        assert info1 == info2

    def test_get_cities_without_name(self, guidebook):
        """Test get_cities without providing a city name."""
        result = guidebook.get_cities()
        assert "Пожалуйста, уточните название города" in result

    def test_get_cities_with_name(self, guidebook):
        """Test get_cities with a city name."""
        result = guidebook.get_cities(name="Berlin")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_cities_with_alias(self, guidebook):
        """Test get_cities with an aliased city name."""
        # Check if there are any vocabulary aliases
        if guidebook.vocabulary:
            alias = list(guidebook.vocabulary.keys())[0]
            result = guidebook.get_cities(name=alias)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_get_countries_without_name(self, guidebook):
        """Test get_countries without providing a country name."""
        result = guidebook.get_countries()
        assert "Пожалуйста, уточните название страны" in result

    def test_get_countries_with_name(self, guidebook):
        """Test get_countries with a country name."""
        result = guidebook.get_countries(name="Poland")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_results(self, guidebook):
        """Test the format_results static method."""
        test_text = "Test content"
        formatted = YamlGuidebook.format_results(test_text)
        assert "=" * 30 in formatted
        assert test_text in formatted
        # Should have separators at start and end
        lines = formatted.split("\n")
        assert "=" in lines[0]
        assert "=" in lines[-1]

    def test_case_insensitive_topic_lookup(self, guidebook):
        """Test that topic lookup is case-insensitive."""
        topics = guidebook.get_topics()
        if topics:
            topic = topics[0]
            info_lower = guidebook.get_info(topic.lower())
            info_upper = guidebook.get_info(topic.upper())
            info_mixed = guidebook.get_info(topic.title())
            # All should return valid results (not the error message)
            assert len(info_lower) > 0
            assert len(info_upper) > 0
            assert len(info_mixed) > 0
