from __future__ import annotations

import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from telegram import Chat, Message, MessageEntity, Update, User
from telegram.ext import Application

os.environ.setdefault("APP_NAME", "TESTING")
os.environ.setdefault("TOKEN", "123:TESTTOKEN")

from src import commands  # noqa: E402

TOKEN = "123:TESTTOKEN"


@pytest.mark.anyio
async def test_application_processes_help_command():
    """End-to-end style test verifying Application dispatches /help."""
    application = Application.builder().token(TOKEN).build()
    commands.register(application)

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
