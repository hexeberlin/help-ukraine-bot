import logging
from functools import wraps
from typing import Dict, Optional

import toml
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from src.guidebook import Guidebook

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

settings: Dict[str, str] = toml.load("settings.toml")

guidebook = Guidebook(
    guidebook_path=settings["GUIDEBOOK_PATH"],
    vocabulary_path=settings["VOCABULARY_PATH"],
)


async def send_results(
    update: Update, context: ContextTypes.DEFAULT_TYPE, group_name: str, name: str = None
) -> None:
    results = f"#{group_name}\n{guidebook.get_info(group_name=group_name, name=name)}"
    await reply_to_message(update, context, results)


async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if not message:
        return
    chat_id = message.chat_id
    message_id = message.message_id
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except BadRequest as e:
        logger.error("BadRequest: %s, chat_id=%s, message=%s", e, chat_id, message)


async def reply_to_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, reply: str, *, disable_web_page_preview: bool = True
) -> None:
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
    # Finally delete the original command.
    await delete_command(update, context)


# Permissions
def restricted(func):
    """A decorator that limits the access to commands only for admins"""

    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat

        if not user or not chat:
            return

        admins = [
            member.user.id
            for member in await context.bot.get_chat_administrators(chat_id=chat.id)
        ]

        if user.id not in admins:
            logger.warning("Non admin attempts to access a restricted function")
            return

        logger.info("Restricted function permission granted")
        return await func(update, context, *args, **kwargs)

    return wrapped


def get_param(update: Update, command: str) -> str:
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
