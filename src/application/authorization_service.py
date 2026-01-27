"""Authorization service - Manages chat access control."""

from typing import Set


class AuthorizationService:
    """Service handling authorization business rules."""

    def __init__(self, admin_only_chat_ids: Set[int]) -> None:
        """
        Initialize the service.

        Args:
            admin_only_chat_ids: Set of chat IDs that are admin-only
        """
        self._admin_only_chat_ids = admin_only_chat_ids.copy()

    def is_admin_only_chat(self, chat_id: int) -> bool:
        """
        Check if chat is admin-only.

        Args:
            chat_id: The chat ID to check

        Returns:
            True if chat is admin-only, False otherwise
        """
        return chat_id in self._admin_only_chat_ids

    def add_admin_only_chat(self, chat_id: int) -> None:
        """
        Add chat to admin-only list.

        Args:
            chat_id: The chat ID to add
        """
        self._admin_only_chat_ids.add(chat_id)

    def remove_admin_only_chat(self, chat_id: int) -> None:
        """
        Remove chat from admin-only list.

        Args:
            chat_id: The chat ID to remove
        """
        self._admin_only_chat_ids.discard(chat_id)

    def get_admin_only_chats(self) -> Set[int]:
        """
        Get copy of admin-only chat IDs.

        Returns:
            Copy of the set of admin-only chat IDs
        """
        return self._admin_only_chat_ids.copy()
