"""Domain protocols - Interfaces for dependency injection."""
from typing import Protocol, List, Dict, Optional, Set, Any


class IGuidebook(Protocol):
    """Protocol for guidebook data access."""

    def get_info(self, group_name: str, name: Optional[str] = None) -> str:
        """Get information for a specific topic."""
        ...

    def get_cities(self, name: Optional[str] = None) -> str:
        """Get city information or prompt for a city."""
        ...

    def get_countries(self, name: Optional[str] = None) -> str:
        """Get country information or prompt for a country."""
        ...

    def get_results(self, group_name: str, name: Optional[str] = None) -> str:
        """Get formatted results for a query."""
        ...

    def get_topics(self) -> List[str]:
        """Get list of all available topics."""
        ...

    def get_descriptions(self) -> Dict[str, str]:
        """Get topic descriptions."""
        ...

    def format_results(self, info: str) -> str:
        """Format results into a readable string."""
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

    def handle_social_reminder(self) -> str:
        """Handle social reminder - return social help information."""
        ...


class IAuthorizationService(Protocol):
    """Protocol for authorization business rules."""

    def is_admin_only_chat(self, chat_id: int) -> bool:
        """Check if chat is admin-only."""
        ...

    def add_admin_only_chat(self, chat_id: int) -> None:
        """Add chat to admin-only list."""
        ...

    def remove_admin_only_chat(self, chat_id: int) -> None:
        """Remove chat from admin-only list."""
        ...

    def get_admin_only_chats(self) -> Set[int]:
        """Get copy of admin-only chat IDs."""
        ...


class IStatisticsService(Protocol):
    """Protocol for request statistics logging."""

    def record_request(
        self,
        user_id: int,
        topic: str,
        *,
        parameter: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None,
    ) -> None:
        """Record a guidebook request."""
        ...

    def top_topics(self, k: int) -> List[tuple[str, int]]:
        """Return top-k topics by request count."""
        ...

    def top_users(self, k: int) -> List[tuple[int, int]]:
        """Return top-k users by request count."""
        ...
