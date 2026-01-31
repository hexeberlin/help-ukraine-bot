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

    def test_get_topic_description_valid_topic(self, guidebook):
        """Test getting description for a valid topic."""
        # accommodation should exist
        description = guidebook.get_topic_description("accommodation")
        assert description is not None
        assert isinstance(description, str)
        assert len(description) > 0

    def test_get_topic_description_case_insensitive(self, guidebook):
        """Test that topic description lookup is case-insensitive."""
        desc_lower = guidebook.get_topic_description("accommodation")
        desc_upper = guidebook.get_topic_description("ACCOMMODATION")
        desc_mixed = guidebook.get_topic_description("Accommodation")

        assert desc_lower == desc_upper == desc_mixed
        assert desc_lower is not None

    def test_get_topic_description_nonexistent_topic(self, guidebook):
        """Test getting description for a nonexistent topic."""
        description = guidebook.get_topic_description("nonexistent_topic")
        assert description is None

    def test_get_topic_contents_list_based(self, guidebook):
        """Test getting contents for a list-based topic."""
        # apartment_approval is a list-based topic
        contents = guidebook.get_topic_contents("apartment_approval")
        assert isinstance(contents, list)
        assert len(contents) > 0
        # All items should be strings
        assert all(isinstance(item, str) for item in contents)

    def test_get_topic_contents_dict_based(self, guidebook):
        """Test getting contents for a dict-based topic."""
        # cities is a dict-based topic
        contents = guidebook.get_topic_contents("cities")
        assert isinstance(contents, dict)
        assert len(contents) > 0
        # Should have Berlin
        assert any("berlin" in key.lower() for key in contents.keys())

    def test_get_topic_contents_case_insensitive(self, guidebook):
        """Test that topic contents lookup is case-insensitive."""
        contents_lower = guidebook.get_topic_contents("cities")
        contents_upper = guidebook.get_topic_contents("CITIES")
        contents_mixed = guidebook.get_topic_contents("Cities")

        assert contents_lower == contents_upper == contents_mixed

    def test_get_topic_contents_nonexistent_topic(self, guidebook):
        """Test that KeyError is raised for nonexistent topic."""
        with pytest.raises(KeyError):
            guidebook.get_topic_contents("nonexistent_topic")

    def test_get_cities_without_name(self, guidebook):
        """Test get_cities without providing a city name."""
        result = guidebook.get_cities()
        assert "Пожалуйста, уточните название города" in result
        # Should be formatted with separators
        assert "=" * 30 in result

    def test_get_cities_with_valid_name(self, guidebook):
        """Test get_cities with a valid city name."""
        result = guidebook.get_cities(name="Berlin")
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain city name
        assert "Berlin" in result or "berlin" in result
        # Should be formatted with separators
        assert "=" * 30 in result

    def test_get_cities_case_insensitive(self, guidebook):
        """Test that city lookup is case-insensitive."""
        result_lower = guidebook.get_cities(name="berlin")
        result_upper = guidebook.get_cities(name="BERLIN")
        result_mixed = guidebook.get_cities(name="Berlin")

        # All should return valid results (not error messages)
        assert "К сожалению" not in result_lower
        assert "К сожалению" not in result_upper
        assert "К сожалению" not in result_mixed

    def test_get_cities_with_alias(self, guidebook):
        """Test get_cities with a vocabulary alias."""
        # Find a vocabulary alias that actually maps to a city
        # The vocabulary includes both cities and countries, so we need to find a valid city alias
        cities_cache = guidebook._lowercase_cache.get("cities", {})
        valid_city_alias = None

        for alias, target in guidebook.vocabulary.items():
            if target in cities_cache:
                valid_city_alias = alias
                break

        if valid_city_alias:
            result = guidebook.get_cities(name=valid_city_alias)
            assert isinstance(result, str)
            assert len(result) > 0
            # Should not be an error message
            assert "К сожалению" not in result
        else:
            # If no city aliases exist, just verify the vocabulary exists
            assert isinstance(guidebook.vocabulary, dict)

    def test_get_cities_nonexistent_city(self, guidebook):
        """Test get_cities with a nonexistent city name."""
        result = guidebook.get_cities(name="NonexistentCity")
        assert "К сожалению, мы пока не располагаем информацией" in result

    def test_get_countries_without_name(self, guidebook):
        """Test get_countries without providing a country name."""
        result = guidebook.get_countries()
        assert "Пожалуйста, уточните название страны" in result
        # Should be formatted with separators
        assert "=" * 30 in result

    def test_get_countries_with_valid_name(self, guidebook):
        """Test get_countries with a valid country name."""
        result = guidebook.get_countries(name="Poland")
        assert isinstance(result, str)
        assert len(result) > 0
        # Should contain country name
        assert "Poland" in result or "poland" in result
        # Should be formatted with separators
        assert "=" * 30 in result

    def test_get_countries_case_insensitive(self, guidebook):
        """Test that country lookup is case-insensitive."""
        result_lower = guidebook.get_countries(name="poland")
        result_upper = guidebook.get_countries(name="POLAND")
        result_mixed = guidebook.get_countries(name="Poland")

        # All should return valid results (not error messages)
        assert "К сожалению" not in result_lower
        assert "К сожалению" not in result_upper
        assert "К сожалению" not in result_mixed

    def test_get_countries_nonexistent_country(self, guidebook):
        """Test get_countries with a nonexistent country name."""
        result = guidebook.get_countries(name="NonexistentCountry")
        assert "К сожалению, мы пока не располагаем информацией" in result

    def test_lowercase_cache_is_populated(self, guidebook):
        """Test that lowercase cache is properly populated for dict topics."""
        # Should have cache for cities (dict topic)
        assert "cities" in guidebook._lowercase_cache
        # Cache should have lowercase keys
        cities_cache = guidebook._lowercase_cache["cities"]
        assert all(key == key.lower() for key in cities_cache.keys())

    def test_vocabulary_loaded(self, guidebook):
        """Test that vocabulary aliases are loaded."""
        assert isinstance(guidebook.vocabulary, dict)
        # All keys and values should be lowercase
        for alias, target in guidebook.vocabulary.items():
            assert alias == alias.lower()
            assert target == target.lower()
