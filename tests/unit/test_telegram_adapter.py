"""Unit tests for TelegramBotAdapter."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch
import pytest
from src.adapters.telegram_adapter import TelegramBotAdapter
from src.domain.protocols import (
    IBerlinHelpService,
    IStatisticsService,
)


@pytest.fixture
def mock_service():
    """Create a mock Berlin help service."""
    service = Mock(spec=IBerlinHelpService)
    service.handle_help.return_value = "Help text"
    service.handle_topic.return_value = "#topic\nTopic info"
    service.handle_cities.return_value = "City info"
    service.handle_countries.return_value = "Country info"
    service.list_topics.return_value = [
        "accommodation",
        "transport",
        "cities",
        "countries",
    ]
    service.get_topic_description.return_value = "Topic description"
    return service


@pytest.fixture
def mock_stats_service():
    """Create a mock statistics service."""
    return Mock(spec=IStatisticsService)


@pytest.fixture
def adapter(
    mock_service,
    mock_stats_service,
):
    """Create a TelegramBotAdapter instance."""
    return TelegramBotAdapter(
        token="test_token",
        service=mock_service,
        stats_service=mock_stats_service,
    )


class TestTelegramBotAdapter:
    """Test TelegramBotAdapter functionality."""

    def test_initialization(self, adapter):
        """Test adapter initialization."""
        assert adapter.token == "test_token"

    def test_build_application(self, adapter):
        """Test building the application."""
        with patch("src.adapters.telegram_adapter.Application") as mock_app_class:
            mock_builder = Mock()
            mock_app = Mock()
            mock_builder.build.return_value = mock_app
            mock_builder.token.return_value = mock_builder
            mock_builder.post_init.return_value = mock_builder
            mock_app_class.builder.return_value = mock_builder

            result = adapter.build_application()

            mock_app_class.builder.assert_called_once()
            mock_builder.token.assert_called_once_with("test_token")
            mock_builder.post_init.assert_called_once()
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
        self, adapter, mock_service, mock_stats_service
    ):
        """Ensure /cities logs stats with topic."""
        adapter._reply_to_message = AsyncMock()
        mock_service.get_topic_description.return_value = "Cities description"
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=42, first_name="User", last_name="FortyTwo"),
            effective_message=SimpleNamespace(text="/cities Berlin", chat_id=123),
        )
        context = SimpleNamespace()

        await adapter._handle_cities(update, context)

        mock_stats_service.record_request.assert_called_once_with(
            topic="cities",
            topic_description="Cities description",
        )

    @pytest.mark.anyio
    async def test_handle_cities_records_stats_username_fallback(
        self, adapter, mock_service, mock_stats_service
    ):
        """Ensure /cities logs stats even when user display name is missing."""
        adapter._reply_to_message = AsyncMock()
        mock_service.get_topic_description.return_value = "Cities description"
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(
                id=42, first_name=None, last_name=None, username="ghost"
            ),
            effective_message=SimpleNamespace(text="/cities Berlin", chat_id=123),
        )
        context = SimpleNamespace()

        await adapter._handle_cities(update, context)

        mock_stats_service.record_request.assert_called_once_with(
            topic="cities",
            topic_description="Cities description",
        )

    @pytest.mark.anyio
    async def test_handle_topic_records_stats(
        self, adapter, mock_service, mock_stats_service
    ):
        """Ensure topic handlers log stats."""
        adapter._reply_to_message = AsyncMock()
        mock_service.get_topic_description.return_value = "Housing info"
        update = SimpleNamespace(
            effective_chat=SimpleNamespace(id=123),
            effective_user=SimpleNamespace(id=7, first_name="User", last_name="Seven"),
            effective_message=SimpleNamespace(text="/accommodation", chat_id=123),
        )
        context = SimpleNamespace()

        handler = adapter._create_topic_handler("accommodation")
        await handler(update, context)

        mock_stats_service.record_request.assert_called_once_with(
            topic="accommodation",
            topic_description="Housing info",
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
