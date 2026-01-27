"""Unit tests for TelegramBotAdapter."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch
import pytest
from src.adapters.telegram_adapter import TelegramBotAdapter
from src.domain.protocols import (
    IBerlinHelpService,
    IAuthorizationService,
    IStatisticsService,
)
from src.adapters.telegram_auth import TelegramAuthorizationAdapter


@pytest.fixture
def mock_service():
    """Create a mock Berlin help service."""
    service = Mock(spec=IBerlinHelpService)
    service.handle_help.return_value = "Help text"
    service.handle_topic.return_value = "#topic\nTopic info"
    service.handle_cities.return_value = "City info"
    service.handle_countries.return_value = "Country info"
    service.handle_social_reminder.return_value = "Social help"
    return service


@pytest.fixture
def mock_auth_service():
    """Create a mock authorization service."""
    auth_service = Mock(spec=IAuthorizationService)
    auth_service.is_admin_only_chat.return_value = False
    return auth_service


@pytest.fixture
def mock_telegram_auth():
    """Create a mock Telegram auth adapter."""
    telegram_auth = Mock(spec=TelegramAuthorizationAdapter)
    telegram_auth.is_user_admin = AsyncMock(return_value=True)
    return telegram_auth


@pytest.fixture
def mock_stats_service():
    """Create a mock statistics service."""
    return Mock(spec=IStatisticsService)


@pytest.fixture
def adapter(mock_service, mock_auth_service, mock_stats_service, mock_telegram_auth):
    """Create a TelegramBotAdapter instance."""
    return TelegramBotAdapter(
        token="test_token",
        service=mock_service,
        guidebook_topics=["accommodation", "transport", "cities", "countries"],
        guidebook_descriptions={
            "accommodation": "Housing info",
            "transport": "Transport info",
        },
        auth_service=mock_auth_service,
        stats_service=mock_stats_service,
        telegram_auth=mock_telegram_auth,
        berlin_chat_ids=[-1001589772550],
        reminder_interval_pinned=30 * 60,
        reminder_interval_info=10 * 60,
        reminder_message="Reminder message",
        pinned_job_name="pinned",
        social_job_name="social",
    )


class TestTelegramBotAdapter:
    """Test TelegramBotAdapter functionality."""

    def test_initialization(self, adapter):
        """Test adapter initialization."""
        assert adapter.token == "test_token"
        assert adapter.reminder_interval_pinned == 30 * 60
        assert adapter.reminder_interval_info == 10 * 60

    def test_build_application(self, adapter):
        """Test building the application."""
        with patch("src.adapters.telegram_adapter.Application") as mock_app_class:
            mock_builder = Mock()
            mock_app = Mock()
            mock_app.job_queue.run_once = Mock()
            mock_builder.build.return_value = mock_app
            mock_builder.token.return_value = mock_builder
            mock_app_class.builder.return_value = mock_builder

            result = adapter.build_application()

            mock_app_class.builder.assert_called_once()
            mock_builder.token.assert_called_once_with("test_token")
            mock_builder.build.assert_called_once()
            assert mock_app.add_handler.called

    def test_extract_parameter_basic(self, adapter):
        """Test extracting parameter from command."""
        update = SimpleNamespace(
            effective_message=SimpleNamespace(text="/cities Berlin")
        )

        result = adapter._extract_parameter(update, "/cities")

        assert result == "berlin"

    def test_extract_parameter_with_bot_name(self, adapter):
        """Test extracting parameter with bot name."""
        update = SimpleNamespace(
            effective_message=SimpleNamespace(text="/cities@botname Berlin")
        )

        result = adapter._extract_parameter(update, "/cities")

        assert result == "berlin"

    def test_extract_parameter_no_param(self, adapter):
        """Test extracting parameter when none provided."""
        update = SimpleNamespace(effective_message=SimpleNamespace(text="/cities"))

        result = adapter._extract_parameter(update, "/cities")

        assert result == ""

    def test_extract_parameter_no_message(self, adapter):
        """Test extracting parameter when no message."""
        update = SimpleNamespace(effective_message=None)

        result = adapter._extract_parameter(update, "/cities")

        assert result == ""

    @pytest.mark.anyio
    async def test_delete_command(self, adapter):
        """Test deleting a command message."""
        update = SimpleNamespace(
            effective_message=SimpleNamespace(chat_id=123, message_id=456)
        )
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._delete_command(update, context)

        context.bot.delete_message.assert_called_once_with(
            chat_id=123, message_id=456
        )

    @pytest.mark.anyio
    async def test_delete_command_no_message(self, adapter):
        """Test deleting command when no message."""
        update = SimpleNamespace(effective_message=None)
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._delete_command(update, context)

        context.bot.delete_message.assert_not_called()

    @pytest.mark.anyio
    async def test_reply_to_message_simple(self, adapter):
        """Test replying to a message."""
        update = SimpleNamespace(
            effective_message=SimpleNamespace(
                chat_id=123, message_id=456, reply_to_message=None
            )
        )
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._reply_to_message(update, context, "Test reply")

        context.bot.send_message.assert_called_once_with(
            chat_id=123, text="Test reply", disable_web_page_preview=True
        )
        context.bot.delete_message.assert_called_once_with(
            chat_id=123, message_id=456
        )

    @pytest.mark.anyio
    async def test_reply_to_message_with_parent(self, adapter):
        """Test replying to a message that itself is a reply."""
        update = SimpleNamespace(
            effective_message=SimpleNamespace(
                chat_id=123,
                message_id=456,
                reply_to_message=SimpleNamespace(message_id=789),
            )
        )
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._reply_to_message(update, context, "Test reply")

        context.bot.send_message.assert_called_once_with(
            chat_id=123,
            reply_to_message_id=789,
            text="Test reply",
            disable_web_page_preview=True,
        )

    @pytest.mark.anyio
    async def test_handle_cities_records_stats(
        self, adapter, mock_stats_service, mock_auth_service
    ):
        """Ensure /cities logs stats with user and topic."""
        mock_auth_service.is_admin_only_chat.return_value = False
        adapter._reply_to_message = AsyncMock()
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=42, username="user42"),
            effective_message=SimpleNamespace(text="/cities Berlin", chat_id=123),
        )
        context = SimpleNamespace()

        await adapter._handle_cities(update, context)

        mock_stats_service.record_request.assert_called_once_with(
            user_id=42,
            user_name="user42",
            topic="cities",
            parameter="berlin",
            extra=None,
        )

    @pytest.mark.anyio
    async def test_handle_topic_records_stats(
        self, adapter, mock_stats_service, mock_auth_service
    ):
        """Ensure topic handlers log stats."""
        mock_auth_service.is_admin_only_chat.return_value = False
        adapter._reply_to_message = AsyncMock()
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=7, username="user7"),
            effective_message=SimpleNamespace(text="/accommodation", chat_id=123),
        )
        context = SimpleNamespace()

        handler = adapter._create_topic_handler("accommodation")
        await handler(update, context)

        mock_stats_service.record_request.assert_called_once_with(
            user_id=7,
            user_name="user7",
            topic="accommodation",
            parameter=None,
            extra=None,
        )

    @pytest.mark.anyio
    async def test_handle_topic_stats_default_k(self, adapter, mock_stats_service):
        """Ensure /topic_stats defaults to k=10."""
        mock_stats_service.top_topics.return_value = [("cities", 2)]
        adapter._reply_to_message = AsyncMock()
        update = SimpleNamespace(
            effective_message=SimpleNamespace(text="/topic_stats", chat_id=123),
            effective_user=SimpleNamespace(id=1),
        )
        context = SimpleNamespace()

        await adapter._handle_topic_stats(update, context)

        mock_stats_service.top_topics.assert_called_once_with(10)

    @pytest.mark.anyio
    async def test_handle_user_stats_custom_k(self, adapter, mock_stats_service):
        """Ensure /user_stats uses provided k."""
        mock_stats_service.top_users.return_value = [(1, 5)]
        adapter._reply_to_message = AsyncMock()
        update = SimpleNamespace(
            effective_message=SimpleNamespace(text="/user_stats 3", chat_id=123),
            effective_user=SimpleNamespace(id=1),
        )
        context = SimpleNamespace()

        await adapter._handle_user_stats(update, context)

        mock_stats_service.top_users.assert_called_once_with(3)

    @pytest.mark.anyio
    async def test_check_access_public_chat(self, adapter, mock_auth_service):
        """Test check_access for public (non-admin-only) chat."""
        mock_auth_service.is_admin_only_chat.return_value = False
        update = SimpleNamespace(effective_chat=SimpleNamespace(id=123))
        context = SimpleNamespace()

        result = await adapter._check_access(update, context)

        assert result is True
        mock_auth_service.is_admin_only_chat.assert_called_once_with(123)

    @pytest.mark.anyio
    async def test_check_access_admin_only_chat_admin_user(
        self, adapter, mock_auth_service, mock_telegram_auth
    ):
        """Test check_access for admin-only chat with admin user."""
        mock_auth_service.is_admin_only_chat.return_value = True
        mock_telegram_auth.is_user_admin = AsyncMock(return_value=True)
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=999),
        )
        context = SimpleNamespace(bot=AsyncMock())

        result = await adapter._check_access(update, context)

        assert result is True

    @pytest.mark.anyio
    async def test_check_access_admin_only_chat_non_admin_user(
        self, adapter, mock_auth_service, mock_telegram_auth
    ):
        """Test check_access for admin-only chat with non-admin user."""
        mock_auth_service.is_admin_only_chat.return_value = True
        mock_telegram_auth.is_user_admin = AsyncMock(return_value=False)
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=999),
        )
        context = SimpleNamespace(bot=AsyncMock())

        result = await adapter._check_access(update, context)

        assert result is False

    @pytest.mark.anyio
    async def test_check_admin_access_admin_user(self, adapter, mock_telegram_auth):
        """Test check_admin_access with admin user."""
        mock_telegram_auth.is_user_admin = AsyncMock(return_value=True)
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=999),
        )
        context = SimpleNamespace(bot=AsyncMock())

        result = await adapter._check_admin_access(update, context)

        assert result is True
        mock_telegram_auth.is_user_admin.assert_called_once_with(
            999, 123, context.bot
        )

    @pytest.mark.anyio
    async def test_check_admin_access_non_admin_user(
        self, adapter, mock_telegram_auth
    ):
        """Test check_admin_access with non-admin user."""
        mock_telegram_auth.is_user_admin = AsyncMock(return_value=False)
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=999),
        )
        context = SimpleNamespace(bot=AsyncMock())

        result = await adapter._check_admin_access(update, context)

        assert result is False

    @pytest.mark.anyio
    async def test_handle_help(self, adapter, mock_service):
        """Test handling /help command."""
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_message=SimpleNamespace(
                chat_id=123, message_id=456, reply_to_message=None, text="/help"
            ),
        )
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._handle_help(update, context)

        mock_service.handle_help.assert_called_once()
        context.bot.send_message.assert_called_once()

    @pytest.mark.anyio
    async def test_handle_cities(self, adapter, mock_service):
        """Test handling /cities command."""
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_message=SimpleNamespace(
                chat_id=123,
                message_id=456,
                reply_to_message=None,
                text="/cities Berlin",
            ),
        )
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._handle_cities(update, context)

        mock_service.handle_cities.assert_called_once_with("berlin", show_all=False)
        context.bot.send_message.assert_called_once()

    @pytest.mark.anyio
    async def test_handle_cities_all(self, adapter, mock_service):
        """Test handling /cities_all command."""
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_message=SimpleNamespace(
                chat_id=123, message_id=456, reply_to_message=None, text="/cities_all"
            ),
        )
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._handle_cities_all(update, context)

        mock_service.handle_cities.assert_called_once_with(None, show_all=True)

    @pytest.mark.anyio
    async def test_handle_countries(self, adapter, mock_service):
        """Test handling /countries command."""
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_message=SimpleNamespace(
                chat_id=123,
                message_id=456,
                reply_to_message=None,
                text="/countries Poland",
            ),
        )
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._handle_countries(update, context)

        mock_service.handle_countries.assert_called_once_with(
            "poland", show_all=False
        )

    @pytest.mark.anyio
    async def test_handle_admins_only(self, adapter, mock_auth_service):
        """Test handling /adminsonly command."""
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=999),
            effective_message=SimpleNamespace(chat_id=123, message_id=456),
        )
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._handle_admins_only(update, context)

        mock_auth_service.add_admin_only_chat.assert_called_once_with(123)
        context.bot.delete_message.assert_called_once()

    @pytest.mark.anyio
    async def test_handle_admins_only_revert(self, adapter, mock_auth_service):
        """Test handling /adminsonly_revert command."""
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=999),
            effective_message=SimpleNamespace(chat_id=123, message_id=456),
        )
        context = SimpleNamespace(bot=AsyncMock())

        await adapter._handle_admins_only_revert(update, context)

        mock_auth_service.remove_admin_only_chat.assert_called_once_with(123)
        context.bot.delete_message.assert_called_once()

    def test_job_name(self, adapter):
        """Test job name generation."""
        result = adapter._job_name("pinned", 123)
        assert result == "pinned-123"

    def test_chat_jobs(self, adapter):
        """Test getting jobs for a chat."""
        job1 = Mock()
        job2 = Mock()
        job_queue = Mock()
        job_queue.get_jobs_by_name.side_effect = [[job1], [job2]]

        result = adapter._chat_jobs(job_queue, 123)

        assert result == [job1, job2]
        assert job_queue.get_jobs_by_name.call_count == 2

    def test_chat_jobs_no_queue(self, adapter):
        """Test getting jobs when no job queue."""
        result = adapter._chat_jobs(None, 123)
        assert result == []
