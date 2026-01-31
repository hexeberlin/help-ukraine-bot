"""Telegram bot adapter - Encapsulates all Telegram-specific logic."""

import logging
from typing import Awaitable, Callable, List

from telegram import BotCommand, Update
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import effective_message_type

from src.domain.protocols import (
    IBerlinHelpService,
    IStatisticsService,
    StatisticsServiceError,
)

logger = logging.getLogger(__name__)


class TelegramBotAdapter:
    """Adapter that encapsulates all Telegram-specific bot logic."""

    def __init__(
        self,
        token: str,
        service: IBerlinHelpService,
        stats_service: IStatisticsService,
    ):
        """
        Initialize the Telegram bot adapter.

        Args:
            token: Telegram bot token
            service: Berlin help service implementation
            stats_service: Statistics service implementation
        """
        self.token = token
        self.service = service
        self.stats_service = stats_service

    def build_application(self) -> Application:
        """
        Build and configure the Telegram Application.

        Returns:
            Configured Application instance
        """
        application = (
            Application.builder()
            .token(self.token)
            .post_init(self._post_init)
            .build()
        )
        self._register_handlers(application)
        return application

    def _register_handlers(self, application: Application) -> None:
        """Register all command handlers with the application."""
        # Basic commands
        application.add_handler(CommandHandler("help", self._handle_help))
        application.add_handler(CommandHandler("topic_stats", self._handle_topic_stats))

        # Dynamic topic handlers
        for topic in self.service.list_topics():
            # Cities and countries are special - handled separately
            if topic not in {"cities", "countries"}:
                application.add_handler(
                    CommandHandler(topic, self._create_topic_handler(topic))
                )

        # Special handlers for cities and countries
        application.add_handler(CommandHandler("cities", self._handle_cities))
        application.add_handler(CommandHandler("countries", self._handle_countries))
        application.add_handler(CommandHandler("cities_all", self._handle_cities_all))
        application.add_handler(
            CommandHandler("countries_all", self._handle_countries_all)
        )

        # Message handler for deleting greetings
        application.add_handler(
            MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS
                | filters.StatusUpdate.LEFT_CHAT_MEMBER,
                self._handle_delete_greetings,
            )
        )

        # Bot commands are set in _post_init to avoid JobQueue dependency.

    # Handler methods
    async def _handle_help(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        results = self.service.handle_help()
        await self._reply_to_message(update, context, results)

    async def _post_init(self, application: Application) -> None:
        """Initialize bot commands after the bot is ready."""
        await application.bot.set_my_commands(self._bot_commands())

    async def _handle_topic_stats(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /topic_stats command (public)."""
        k = self._extract_k_parameter(update, "/topic_stats")
        rows = self.stats_service.top_topics(k)
        reply = self._format_topic_stats(rows, k)
        await self._reply_to_message(update, context, reply)

    def _create_topic_handler(
        self, topic: str
    ) -> Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]:
        """Create a handler for a specific topic."""

        async def handler(
            update: Update, context: ContextTypes.DEFAULT_TYPE
        ) -> None:
            results = self.service.handle_topic(topic)
            self._record_stats(topic)
            await self._reply_to_message(update, context, results)

        return handler

    async def _handle_cities(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /cities command."""
        city_name = self._extract_parameter(update, "/cities")
        results = self.service.handle_cities(city_name, show_all=False)
        self._record_stats("cities")
        await self._reply_to_message(update, context, results)

    async def _handle_cities_all(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /cities_all command."""
        results = self.service.handle_cities(None, show_all=True)
        self._record_stats("cities")
        await self._reply_to_message(update, context, results)

    async def _handle_countries(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /countries command."""
        country_name = self._extract_parameter(update, "/countries")
        results = self.service.handle_countries(country_name, show_all=False)
        self._record_stats("countries")
        await self._reply_to_message(update, context, results)

    async def _handle_countries_all(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /countries_all command."""
        results = self.service.handle_countries(None, show_all=True)
        self._record_stats("countries")
        await self._reply_to_message(update, context, results)

    async def _handle_delete_greetings(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Delete join/left notifications to keep chats tidy."""
        message = update.effective_message
        if message:
            msg_type = effective_message_type(message)
            logger.debug("Handling type is %s", msg_type)
            if msg_type in [
                "new_chat_members",
                "left_chat_member",
            ]:
                await self._delete_command(update, context)

    # Utility methods
    def _extract_parameter(self, update: Update, command: str) -> str:
        """
        Extract parameter from command message.

        Args:
            update: The Telegram update
            command: The command string (e.g., "/cities")

        Returns:
            The parameter string, or empty string if none
        """
        message = update.effective_message
        if not message or not message.text:
            return ""

        text = message.text.strip().lower()
        if not text.startswith(command):
            return text

        remainder = text[len(command) :]
        if remainder.startswith("@"):
            remainder = remainder.split(maxsplit=1)
            remainder = remainder[1] if len(remainder) > 1 else ""
        return remainder.strip()

    def _extract_k_parameter(self, update: Update, command: str) -> int:
        raw = self._extract_parameter(update, command)
        if not raw:
            return 10
        try:
            k = int(raw)
        except ValueError:
            return 10
        return max(1, k)

    def _bot_commands(self) -> List[BotCommand]:
        commands = []

        # Add commands for all topics except cities and countries
        for topic in self.service.list_topics():
            if topic not in {"cities", "countries"}:
                description = self.service.get_topic_description(topic)
                if description:
                    commands.append(BotCommand(topic, description))

        # Add special commands for cities and countries
        commands.extend([
            BotCommand(
                "cities",
                "Чаты помощи по городам Германии (введите /cities ГОРОД)",
            ),
            BotCommand(
                "cities_all",
                "Список всех чатов по городам Германии",
            ),
            BotCommand("countries", "Чаты по странам (введите /countries СТРАНА)"),
            BotCommand("countries_all", "Список всех чатов по странам"),
            BotCommand("topic_stats", "Топ тем по количеству запросов"),
        ])

        return commands

    def _format_topic_stats(self, rows: List[tuple[str, int]], k: int) -> str:
        if not rows:
            return "No topic statistics yet."
        lines = [f"Top {k} topics:"]
        for idx, (topic_desc, count) in enumerate(rows, start=1):
            lines.append(f"{idx}. {topic_desc} — {count}")
        return "\n".join(lines)

    def _record_stats(self, topic: str) -> None:
        try:
            self.stats_service.record_request(
                topic=topic,
                topic_description=self.service.get_topic_description(topic),
            )
        except StatisticsServiceError:
            logger.exception("Failed to record stats for topic %s", topic)

    async def _reply_to_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        reply: str,
        *,
        disable_web_page_preview: bool = True
    ) -> None:
        """
        Send a reply and delete the command message.

        Args:
            update: The Telegram update
            context: The context
            reply: The reply text
            disable_web_page_preview: Whether to disable web page preview
        """
        message = update.effective_message
        if not message:
            return

        chat_id = message.chat_id

        if message.reply_to_message is None:
            await context.bot.send_message(
                chat_id=chat_id,
                text=reply,
                disable_web_page_preview=disable_web_page_preview,
            )
        else:
            parent_message_id = message.reply_to_message.message_id
            await context.bot.send_message(
                chat_id=chat_id,
                reply_to_message_id=parent_message_id,
                text=reply,
                disable_web_page_preview=disable_web_page_preview,
            )

        # Finally delete the original command
        await self._delete_command(update, context)

    async def _delete_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Delete the command message."""
        message = update.effective_message
        if not message:
            return

        chat_id = message.chat_id
        message_id = message.message_id

        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except BadRequest as e:
            logger.error("BadRequest: %s, chat_id=%s, message=%s", e, chat_id, message)
