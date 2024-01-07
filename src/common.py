import logging
from functools import wraps
from typing import Dict, List, Optional

import toml
from telegram import Bot, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from src.guidebook import Guidebook
from src.models import Article

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

settings: Dict[str, str] = toml.load("settings.toml")

guidebook = Guidebook(
    guidebook_path=settings["GUIDEBOOK_PATH"],
    vocabulary_path=settings["VOCABULARY_PATH"],
)


def send_results(bot: Bot, update: Update, group_name: str, name: str = None):
    results = f"#{group_name}\n{guidebook.get_info(group_name=group_name, name=name)}"
    reply_to_message(bot, update, results)


def delete_command(bot: Bot, update: Update) -> None:
    message = update.message
    chat_id = message.chat_id
    command_message_id = message.message_id
    try:
        bot.delete_message(chat_id=chat_id, message_id=command_message_id)
    except BadRequest as e:
        logger.info("BadRequest: %s", str(e))


def reply_to_message(bot, update, reply, disable_web_page_preview=True) -> None:
    message = update.message
    chat_id = message.chat_id

    if message.reply_to_message is None:
        bot.send_message(
            chat_id=chat_id,
            text=reply,
            disable_web_page_preview=disable_web_page_preview,
        )
    else:
        parent_message_id = message.reply_to_message.message_id
        bot.send_message(
            chat_id=chat_id,
            reply_to_message_id=parent_message_id,
            text=reply,
            disable_web_page_preview=disable_web_page_preview,
        )
    # Finally delete the original command.
    delete_command(bot, update)


# Permissions
def restricted(func):
    """A decorator that limits the access to commands only for admins"""

    @wraps(func)
    def wrapped(bot: Bot, context: CallbackContext, *args, **kwargs):
        user_id = context.effective_user.id
        chat_id = context.effective_chat.id
        admins = [u.user.id for u in bot.get_chat_administrators(chat_id)]

        if user_id not in admins:
            logger.warning("Non admin attempts to access a restricted function")
            return

        logger.info("Restricted function permission granted")
        return func(bot, context, *args, **kwargs)

    return wrapped


def get_param(bot, update, command):
    bot_name = bot.name
    return (
        update.message.text.removeprefix(command).replace(bot_name, "").strip().lower()
    )


def parse_keys(line: str) -> List[str]:
    keys = line.split(" ")
    non_empty_keys = list(filter(lambda x: x.strip() != "", keys))
    return non_empty_keys


def parse_article(message: str, command: str, bot_name: str) -> Optional[Article]:
    message = message.removeprefix(command).replace(bot_name, "")
    lines = message.splitlines()
    if len(lines) < 3:
        return None
    else:
        keys = parse_keys(lines[0])
        if len(keys) < 1:
            return None
        else:
            title = lines[1]
            content = "".join(lines[2:])
            return Article(keys, title, content)


def format_knowledge_results(results: str) -> str:
    separator = "=" * 30
    return separator + "\n" + results + "\n" + separator
