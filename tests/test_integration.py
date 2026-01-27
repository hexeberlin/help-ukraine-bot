from __future__ import annotations

import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from telegram import Chat, Message, MessageEntity, Update, User

os.environ.setdefault("APP_NAME", "TESTING")
os.environ.setdefault("TOKEN", "123:TESTTOKEN")

from src.infrastructure.yaml_guidebook import YamlGuidebook  # noqa: E402
from src.application.berlin_help_service import BerlinHelpService  # noqa: E402
from src.application.authorization_service import AuthorizationService  # noqa: E402
from src.adapters.telegram_auth import TelegramAuthorizationAdapter  # noqa: E402
from src.adapters.telegram_adapter import TelegramBotAdapter  # noqa: E402

TOKEN = "123:TESTTOKEN"


@pytest.mark.anyio
async def test_application_processes_help_command():
    """End-to-end style test verifying Application dispatches /help using new architecture."""
    # Set up the new architecture
    guidebook = YamlGuidebook(
        guidebook_path="src/knowledgebase/guidebook.yml",
        vocabulary_path="src/knowledgebase/vocabulary.yml"
    )
    service = BerlinHelpService(guidebook=guidebook)
    auth_service = AuthorizationService(admin_only_chat_ids=set())
    telegram_auth = TelegramAuthorizationAdapter()

    adapter = TelegramBotAdapter(
        token=TOKEN,
        service=service,
        guidebook_topics=guidebook.get_topics(),
        guidebook_descriptions=guidebook.get_descriptions(),
        auth_service=auth_service,
        telegram_auth=telegram_auth,
        berlin_chat_ids=[],
        reminder_interval_pinned=30 * 60,
        reminder_interval_info=10 * 60,
        reminder_message="Test reminder",
        pinned_job_name="pinned",
        social_job_name="social",
    )

    application = adapter.build_application()

    # Avoid network calls and record outgoing bot operations.
    bot = application.bot
    bot._unfreeze()
    bot.delete_webhook = AsyncMock()
    bot_user = User(
        id=99999, is_bot=True, first_name="Helper", username="helperbot"
    )

    async def fake_get_me(*args, **kwargs):
        bot._bot_user = bot_user
        return bot_user

    bot.get_me = fake_get_me
    bot.send_message = AsyncMock()
    bot.delete_message = AsyncMock()
    bot._freeze()
    application.updater = None

    async with application:
        chat = Chat(id=999, type="group")
        user = User(id=12345, is_bot=False, first_name="Integration")
        message = Message(
            message_id=1,
            date=datetime.now(timezone.utc),
            chat=chat,
            from_user=user,
            text="/help",
            entities=[MessageEntity(type="bot_command", offset=0, length=5)],
        )
        message.set_bot(application.bot)
        update = Update(update_id=1, message=message)
        await application.process_update(update)

    application.bot.send_message.assert_awaited()
    application.bot.delete_message.assert_awaited()
