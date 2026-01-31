"""YAML-based guidebook implementation."""

import logging
from typing import Any, Dict, List, Optional

from yaml import safe_load

from src.domain.protocols import GuidebookContent
from src.infrastructure.guidebook_formatter import format_contents, wrap_with_separator

logger = logging.getLogger(__name__)


class YamlGuidebook:
    """YAML-based implementation of guidebook data access."""

    def __init__(self, guidebook_path: str, vocabulary_path: str) -> None:
        """Initialize the guidebook from YAML files.

        Args:
            guidebook_path: Path to guidebook.yml
            vocabulary_path: Path to vocabulary.yml (aliases for cities)
        """
        with open(guidebook_path, "r", encoding="utf-8") as f:
            raw_guidebook: Dict[str, Dict[str, Any]] = safe_load(f)

        # Store topics as unified structures: {topic_name: {description: ..., contents: ...}}
        # Topic names are stored in lowercase for case-insensitive lookups
        self.topics: Dict[str, Dict[str, Any]] = {
            topic_name.lower(): {
                "description": topic_data.get("description", "") or "",
                "contents": topic_data.get("contents")
            }
            for topic_name, topic_data in raw_guidebook.items()
        }

        # Cache lowercase versions of dict keys for case-insensitive subtopic/section lookups
        # This is used for all dict-based topics (cities, countries, animals, etc.)
        self._lowercase_cache: Dict[str, Dict[str, List[str]]] = {
            topic_name: {
                key.lower(): value
                for key, value in topic_info["contents"].items()
            }
            for topic_name, topic_info in self.topics.items()
            if isinstance(topic_info["contents"], dict)
        }

        # Load vocabulary aliases (currently only used for cities)
        with open(vocabulary_path, "r", encoding="utf-8") as f:
            self.vocabulary: Dict[str, str] = {
                alias.lower(): name.lower()
                for name, aliases in safe_load(f).items()
                for alias in aliases
            }

    def get_topic_description(self, topic: str) -> Optional[str]:
        """Get the description for a given topic.

        Args:
            topic: Topic name (case-insensitive)

        Returns:
            Topic description string, or None if topic doesn't exist
        """
        topic_info = self.topics.get(topic.lower())
        if topic_info:
            return topic_info["description"]
        return None

    def get_topic_contents(self, topic: str) -> GuidebookContent:
        """Get the contents for a given topic.

        Args:
            topic: Topic name (case-insensitive)

        Returns:
            Contents as either a list of strings or a dict mapping keys to lists

        Raises:
            KeyError: If topic doesn't exist
        """
        topic_lower = topic.lower()
        if topic_lower not in self.topics:
            raise KeyError(f"Topic '{topic}' not found")

        return self.topics[topic_lower]["contents"]

    def get_topics(self) -> List[str]:
        """Get list of all available topics.

        Returns:
            List of topic names (lowercase)
        """
        return list(self.topics.keys())

    def get_cities(self, name: Optional[str] = None) -> str:
        """Get city information or prompt for a city.

        Special handler for cities with formatting and vocabulary alias support.

        Args:
            name: City name (optional, case-insensitive)

        Returns:
            Formatted city information or prompt message
        """
        if not name:
            return wrap_with_separator(
                "Пожалуйста, уточните название города: /cities Name\n"
            )

        # Resolve vocabulary alias if present
        name_lower = name.lower()
        if name_lower in self.vocabulary:
            name_lower = self.vocabulary[name_lower]

        # Look up city in lowercase cache
        cities_cache = self._lowercase_cache.get("cities", {})
        if name_lower not in cities_cache:
            return (
                "К сожалению, мы пока не располагаем информацией "
                f"по запросу cities, {name}."
            )

        # Format city contents with title
        city_contents = cities_cache[name_lower]
        return format_contents(city_contents, title=name)

    def get_countries(self, name: Optional[str] = None) -> str:
        """Get country information or prompt for a country.

        Special handler for countries with formatting.

        Args:
            name: Country name (optional, case-insensitive)

        Returns:
            Formatted country information or prompt message
        """
        if not name:
            return wrap_with_separator(
                "Пожалуйста, уточните название страны: /countries Name\n"
            )

        # Look up country in lowercase cache
        name_lower = name.lower()
        countries_cache = self._lowercase_cache.get("countries", {})
        if name_lower not in countries_cache:
            return (
                "К сожалению, мы пока не располагаем информацией "
                f"по запросу countries, {name}."
            )

        # Format country contents with title
        country_contents = countries_cache[name_lower]
        return format_contents(country_contents, title=name)
