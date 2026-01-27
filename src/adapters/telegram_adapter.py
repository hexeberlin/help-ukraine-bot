"""Telegram bot adapter - Encapsulates all Telegram-specific logic."""

import logging
from typing import Awaitable, Callable, List, Optional

from telegram import BotCommand, Message, Update
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    Job,
    JobQueue,
    MessageHandler,
    filters,
)
from telegram.helpers import effective_message_type

from src.domain.protocols import (
    IBerlinHelpService,
    IAuthorizationService,
    IStatisticsService,
)
from src.adapters.telegram_auth import TelegramAuthorizationAdapter

logger = logging.getLogger(__name__)


class TelegramBotAdapter:
    """Adapter that encapsulates all Telegram-specific bot logic."""

    def __init__(
        self,
        token: str,
        service: IBerlinHelpService,
        guidebook_topics: List[str],
        guidebook_descriptions: dict,
        auth_service: IAuthorizationService,
        stats_service: IStatisticsService,
        telegram_auth: TelegramAuthorizationAdapter,
        berlin_chat_ids: List[int],
        reminder_interval_pinned: int,
        reminder_interval_info: int,
        reminder_message: str,
        pinned_job_name: str,
        social_job_name: str,
    ):
        """
        Initialize the Telegram bot adapter.

        Args:
            token: Telegram bot token
            service: Berlin help service implementation
            guidebook_topics: List of available topics
            guidebook_descriptions: Dictionary of topic descriptions
            auth_service: Authorization service implementation
            telegram_auth: Telegram authorization adapter
            berlin_chat_ids: List of Berlin-specific chat IDs for reminders
            reminder_interval_pinned: Interval for pinned message reminders (seconds)
            reminder_interval_info: Interval for info reminders (seconds)
            reminder_message: Default reminder message text
            pinned_job_name: Job name prefix for pinned reminders
            social_job_name: Job name prefix for social reminders
        """
        self.token = token
        self.service = service
        self.guidebook_topics = guidebook_topics
        self.guidebook_descriptions = guidebook_descriptions
        self.auth_service = auth_service
        self.stats_service = stats_service
        self.telegram_auth = telegram_auth
        self.berlin_chat_ids = berlin_chat_ids
        self.reminder_interval_pinned = reminder_interval_pinned
        self.reminder_interval_info = reminder_interval_info
        self.reminder_message = reminder_message
        self.pinned_job_name = pinned_job_name
        self.social_job_name = social_job_name

    def build_application(self) -> Application:
        """
        Build and configure the Telegram Application.

        Returns:
            Configured Application instance
        """
        application = Application.builder().token(self.token).build()
        self._register_handlers(application)
        return application

    def _register_handlers(self, application: Application) -> None:
        """Register all command handlers with the application."""
        # Basic commands
        application.add_handler(CommandHandler("start", self._handle_start_timer))
        application.add_handler(CommandHandler("stop", self._handle_stop_timer))
        application.add_handler(CommandHandler("help", self._handle_help))
        application.add_handler(CommandHandler("topic_stats", self._handle_topic_stats))
        application.add_handler(CommandHandler("user_stats", self._handle_user_stats))

        # Admin commands
        application.add_handler(CommandHandler("adminsonly", self._handle_admins_only))
        application.add_handler(
            CommandHandler("adminsonly_revert", self._handle_admins_only_revert)
        )

        # Dynamic topic handlers
        for topic in self.guidebook_topics:
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

        # Set bot commands for UI
        all_commands = [
            BotCommand(topic, description)
            for topic, description in self.guidebook_descriptions.items()
            if topic not in {"cities", "countries"}
        ] + [
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
            BotCommand("user_stats", "Топ пользователей по количеству запросов"),
        ]

        # Schedule the set_my_commands call after the bot is initialized
        if application.job_queue:
            application.job_queue.run_once(
                lambda context: context.bot.set_my_commands(all_commands),
                when=0,
            )

    # Handler methods
    async def _handle_help(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /help command."""
        if not await self._check_access(update, context):
            return
        results = self.service.handle_help()
        await self._reply_to_message(update, context, results)

    async def _handle_topic_stats(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /topic_stats command (public)."""
        k = self._extract_k_parameter(update, "/topic_stats")
        rows = self.stats_service.top_topics(k)
        reply = self._format_topic_stats(rows, k)
        await self._reply_to_message(update, context, reply)

    async def _handle_user_stats(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /user_stats command (public)."""
        k = self._extract_k_parameter(update, "/user_stats")
        rows = self.stats_service.top_users(k)
        reply = self._format_user_stats(rows, k)
        await self._reply_to_message(update, context, reply)

    def _create_topic_handler(
        self, topic: str
    ) -> Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]:
        """Create a handler for a specific topic."""

        async def handler(
            update: Update, context: ContextTypes.DEFAULT_TYPE
        ) -> None:
            if not await self._check_access(update, context):
                return
            results = self.service.handle_topic(topic)
            self._record_stats(update, topic, parameter=None)
            await self._reply_to_message(update, context, results)

        return handler

    async def _handle_cities(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /cities command."""
        if not await self._check_access(update, context):
            return
        city_name = self._extract_parameter(update, "/cities")
        results = self.service.handle_cities(city_name, show_all=False)
        self._record_stats(update, "cities", parameter=city_name or None)
        await self._reply_to_message(update, context, results)

    async def _handle_cities_all(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /cities_all command."""
        if not await self._check_access(update, context):
            return
        results = self.service.handle_cities(None, show_all=True)
        self._record_stats(update, "cities", parameter=None, extra={"show_all": True})
        await self._reply_to_message(update, context, results)

    async def _handle_countries(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /countries command."""
        if not await self._check_access(update, context):
            return
        country_name = self._extract_parameter(update, "/countries")
        results = self.service.handle_countries(country_name, show_all=False)
        self._record_stats(update, "countries", parameter=country_name or None)
        await self._reply_to_message(update, context, results)

    async def _handle_countries_all(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /countries_all command."""
        if not await self._check_access(update, context):
            return
        results = self.service.handle_countries(None, show_all=True)
        self._record_stats(
            update, "countries", parameter=None, extra={"show_all": True}
        )
        await self._reply_to_message(update, context, results)

    async def _handle_start_timer(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /start command - start reminder timers."""
        if not await self._check_admin_access(update, context):
            return

        message = update.effective_message
        if not message:
            return

        chat_id = message.chat_id
        if chat_id in self.berlin_chat_ids:
            await self._start_reminder(update, context)

        await self._delete_command(update, context)

    async def _handle_stop_timer(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /stop command - stop reminder timers."""
        if not await self._check_admin_access(update, context):
            return

        chat = update.effective_chat
        if not chat:
            return

        chat_id = chat.id
        job_queue = context.job_queue
        if job_queue is None:
            logger.warning("Job queue not configured; cannot stop reminders.")
            return

        jobs = self._chat_jobs(job_queue, chat_id)

        if jobs:
            await context.bot.send_message(
                chat_id=chat_id, text="I'm stopping sending the reminders."
            )

        # Stop already existing jobs
        for job in jobs:
            job.enabled = False

        logger.info("Stopped reminders in channel %s", chat_id)

    async def _handle_admins_only(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /adminsonly command - restrict chat to admins."""
        if not await self._check_admin_access(update, context):
            return

        chat = update.effective_chat
        if not chat:
            return

        chat_id = chat.id
        self.auth_service.add_admin_only_chat(chat_id)
        await self._delete_command(update, context)

    async def _handle_admins_only_revert(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Handle /adminsonly_revert command - remove admin-only restriction."""
        if not await self._check_admin_access(update, context):
            return

        chat = update.effective_chat
        if not chat:
            return

        chat_id = chat.id
        self.auth_service.remove_admin_only_chat(chat_id)
        await self._delete_command(update, context)

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

    # Authorization methods
    async def _check_access(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> bool:
        """
        Check if user has access (considering admin-only chats).

        Returns:
            True if user has access, False otherwise
        """
        chat = update.effective_chat
        if not chat:
            return False

        # If chat is not admin-only, everyone has access
        if not self.auth_service.is_admin_only_chat(chat.id):
            return True

        # If chat is admin-only, check if user is admin
        return await self._check_admin_access(update, context)

    async def _check_admin_access(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> bool:
        """
        Check if user is an admin.

        Returns:
            True if user is admin, False otherwise
        """
        user = update.effective_user
        chat = update.effective_chat

        if not user or not chat:
            return False

        is_admin = await self.telegram_auth.is_user_admin(
            user.id, chat.id, context.bot
        )

        if not is_admin:
            logger.warning("Non admin attempts to access a restricted function")
            return False

        logger.info("Restricted function permission granted")
        return True

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

    def _format_topic_stats(self, rows: List[tuple[str, int]], k: int) -> str:
        if not rows:
            return "No topic statistics yet."
        lines = [f"Top {k} topics:"]
        for idx, (topic, count) in enumerate(rows, start=1):
            lines.append(f"{idx}. {topic} — {count}")
        return "\n".join(lines)

    def _format_user_stats(self, rows: List[tuple[int, int]], k: int) -> str:
        if not rows:
            return "No user statistics yet."
        lines = [f"Top {k} users:"]
        for idx, (user_id, count) in enumerate(rows, start=1):
            lines.append(f"{idx}. {user_id} — {count}")
        return "\n".join(lines)

    def _record_stats(
        self,
        update: Update,
        topic: str,
        *,
        parameter: Optional[str],
        extra: Optional[dict] = None,
    ) -> None:
        user = getattr(update, "effective_user", None)
        if not user:
            return
        self.stats_service.record_request(
            user_id=user.id, topic=topic, parameter=parameter, extra=extra
        )

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

    # Reminder methods
    async def _start_reminder(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Start reminder jobs for a chat."""
        message = update.effective_message
        if not message:
            return

        chat_id = message.chat_id
        job_queue = context.job_queue
        if job_queue is None:
            logger.warning("Job queue not configured; reminders cannot be scheduled.")
            return

        logger.info("Started reminders in channel %s", chat_id)

        jobs = self._chat_jobs(job_queue, chat_id)

        # Restart already existing jobs
        for job in jobs:
            if not job.enabled:
                job.enabled = True

        # Start a new job if there was none previously
        if not jobs:
            await self._add_pinned_reminder_job(context, chat_id)
            await self._add_info_job(context, chat_id)

    async def _add_pinned_reminder_job(
        self, context: ContextTypes.DEFAULT_TYPE, chat_id: int
    ) -> None:
        """Add a job to send pinned message reminders."""
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"I'm starting sending the pinned reminder every {self.reminder_interval_pinned}s.",
        )
        job_queue = context.job_queue
        if job_queue is None:
            return

        job_queue.run_repeating(
            self._send_pinned_reminder,
            interval=self.reminder_interval_pinned,
            first=1,
            chat_id=chat_id,
            name=self._job_name(self.pinned_job_name, chat_id),
            data={"chat_id": chat_id},
        )

    async def _add_info_job(
        self, context: ContextTypes.DEFAULT_TYPE, chat_id: int
    ) -> None:
        """Add a job to send info reminders."""
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"I'm starting sending the info reminder every {self.reminder_interval_info}s.",
        )
        job_queue = context.job_queue
        if job_queue is None:
            return

        job_queue.run_repeating(
            self._send_social_reminder,
            interval=self.reminder_interval_info,
            first=1,
            chat_id=chat_id,
            name=self._job_name(self.social_job_name, chat_id),
            data={"chat_id": chat_id},
        )

    async def _send_pinned_reminder(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a reminder with the pinned message."""
        job = context.job
        if job is None:
            return

        chat_id = job.chat_id
        chat = await context.bot.get_chat(chat_id)
        msg: Optional[Message] = chat.pinned_message
        logger.info("Sending pinned message to chat %s", chat_id)

        if msg:
            await context.bot.forward_message(
                chat_id=chat_id, from_chat_id=chat_id, message_id=msg.message_id
            )
        else:
            await context.bot.send_message(chat_id=chat_id, text=self.reminder_message)

    async def _send_social_reminder(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a social help reminder."""
        job = context.job
        if job is None:
            return

        chat_id = job.chat_id
        logger.info("Sending a social reminder to chat %s", chat_id)
        results = self.service.handle_social_reminder()
        await context.bot.send_message(
            chat_id=chat_id, text=results, disable_web_page_preview=True
        )

    # Job management helpers
    def _job_name(self, job_type: str, chat_id: int) -> str:
        """Generate a job name for a chat."""
        return f"{job_type}-{chat_id}"

    def _chat_jobs(self, job_queue: Optional[JobQueue], chat_id: int) -> List[Job]:
        """Get all jobs for a specific chat."""
        if job_queue is None:
            return []

        jobs: List[Job] = []
        for job_type in (self.pinned_job_name, self.social_job_name):
            jobs.extend(job_queue.get_jobs_by_name(self._job_name(job_type, chat_id)))
        return jobs
