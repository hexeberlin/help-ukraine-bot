"""Unit tests for AuthorizationService."""

import pytest
from src.application.authorization_service import AuthorizationService


@pytest.fixture
def service():
    """Create an AuthorizationService with initial admin-only chats."""
    return AuthorizationService(admin_only_chat_ids={-1001723117571, -735136184})


class TestAuthorizationService:
    """Test AuthorizationService functionality."""

    def test_initialization(self, service):
        """Test service is initialized with correct chat IDs."""
        chats = service.get_admin_only_chats()
        assert -1001723117571 in chats
        assert -735136184 in chats
        assert len(chats) == 2

    def test_is_admin_only_chat_positive(self, service):
        """Test is_admin_only_chat returns True for admin-only chat."""
        assert service.is_admin_only_chat(-1001723117571) is True
        assert service.is_admin_only_chat(-735136184) is True

    def test_is_admin_only_chat_negative(self, service):
        """Test is_admin_only_chat returns False for non-admin-only chat."""
        assert service.is_admin_only_chat(12345) is False
        assert service.is_admin_only_chat(-99999) is False

    def test_add_admin_only_chat(self, service):
        """Test adding a chat to admin-only list."""
        new_chat_id = -999888777
        assert service.is_admin_only_chat(new_chat_id) is False

        service.add_admin_only_chat(new_chat_id)

        assert service.is_admin_only_chat(new_chat_id) is True
        assert new_chat_id in service.get_admin_only_chats()

    def test_add_admin_only_chat_duplicate(self, service):
        """Test adding a chat that's already admin-only."""
        original_count = len(service.get_admin_only_chats())

        service.add_admin_only_chat(-1001723117571)

        # Should not add duplicate
        assert len(service.get_admin_only_chats()) == original_count
        assert service.is_admin_only_chat(-1001723117571) is True

    def test_remove_admin_only_chat(self, service):
        """Test removing a chat from admin-only list."""
        assert service.is_admin_only_chat(-735136184) is True

        service.remove_admin_only_chat(-735136184)

        assert service.is_admin_only_chat(-735136184) is False
        assert -735136184 not in service.get_admin_only_chats()

    def test_remove_admin_only_chat_nonexistent(self, service):
        """Test removing a chat that's not in admin-only list."""
        original_count = len(service.get_admin_only_chats())

        # Should not raise error
        service.remove_admin_only_chat(-999999)

        # Count should remain the same
        assert len(service.get_admin_only_chats()) == original_count

    def test_get_admin_only_chats_returns_copy(self, service):
        """Test that get_admin_only_chats returns a copy (immutability)."""
        chats1 = service.get_admin_only_chats()
        original_len = len(chats1)

        # Modify the returned set
        chats1.add(-123456)

        # Get a new copy
        chats2 = service.get_admin_only_chats()

        # Original should not be affected
        assert len(chats2) == original_len
        assert -123456 not in chats2

    def test_initialization_with_empty_set(self):
        """Test initialization with empty set."""
        service = AuthorizationService(admin_only_chat_ids=set())

        assert len(service.get_admin_only_chats()) == 0
        assert service.is_admin_only_chat(12345) is False

    def test_initialization_makes_copy(self):
        """Test that initialization makes a copy of the input set."""
        original_set = {-1001723117571, -735136184}
        service = AuthorizationService(admin_only_chat_ids=original_set)

        # Modify original set
        original_set.add(-999999)

        # Service should not be affected
        assert -999999 not in service.get_admin_only_chats()
        assert len(service.get_admin_only_chats()) == 2
