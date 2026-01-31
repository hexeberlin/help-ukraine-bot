"""Domain protocols - Interfaces for dependency injection."""
from typing import Protocol, List, Dict, Optional, Union

# Type alias for guidebook content (can be a list or dict)
GuidebookContent = Union[List[str], Dict[str, List[str]]]


class StatisticsServiceError(Exception):
    """Raised when statistics logging fails."""
    ...


class IGuidebook(Protocol):
    """Protocol for guidebook data access.

    Note: Formatting is handled by higher layers (e.g., guidebook_formatter module).
    This protocol focuses on data access only.
    """

    def get_topic_description(self, topic: str) -> Optional[str]:
        """Get the description for a given topic.

        Args:
            topic: Topic name (case-insensitive)

        Returns:
            Topic description string, or None if topic doesn't exist
        """
        ...

    def get_topic_contents(self, topic: str) -> GuidebookContent:
        """Get the contents for a given topic.

        Args:
            topic: Topic name (case-insensitive)

        Returns:
            Contents as either a list of strings or a dict mapping keys to lists.
            For topics like 'cities' and 'countries', returns all subtopics.

        Raises:
            KeyError: If topic doesn't exist
        """
        ...

    def get_topics(self) -> List[str]:
        """Get list of all available topics."""
        ...

    def get_cities(self, name: Optional[str] = None) -> str:
        """Get city information or prompt for a city.

        Special handler for cities with formatting and vocabulary alias support.

        Args:
            name: City name (optional, case-insensitive)

        Returns:
            Formatted city information or prompt message
        """
        ...

    def get_countries(self, name: Optional[str] = None) -> str:
        """Get country information or prompt for a country.

        Special handler for countries with formatting.

        Args:
            name: Country name (optional, case-insensitive)

        Returns:
            Formatted country information or prompt message
        """
        ...


class IBerlinHelpService(Protocol):
    """Protocol for Berlin help business logic."""

    def handle_help(self) -> str:
        """Handle help command - return help text with available topics."""
        ...

    def handle_topic(self, topic_name: str) -> str:
        """Handle topic request - return formatted topic information."""
        ...

    def handle_cities(self, city_name: Optional[str], show_all: bool = False) -> str:
        """Handle cities command - return city information."""
        ...

    def handle_countries(self, country_name: Optional[str], show_all: bool = False) -> str:
        """Handle countries command - return country information."""
        ...

    def list_topics(self) -> List[str]:
        """Return list of all available topic names.

        Returns:
            List of topic names (lowercase)
        """
        ...

    def get_topic_description(self, topic: str) -> Optional[str]:
        """Get the description for a given topic.

        Args:
            topic: Topic name (case-insensitive)

        Returns:
            Topic description string, or None if topic doesn't exist
        """
        ...


class IStatisticsService(Protocol):
    """Protocol for request statistics logging."""

    def record_request(
        self,
        topic: str,
        *,
        topic_description: Optional[str] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        """Record a guidebook request."""
        ...

    def top_topics(self, k: int) -> List[tuple[str, int]]:
        """Return top-k topic descriptions by request count."""
        ...
