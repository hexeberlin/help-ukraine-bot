import logging

from telegram import Bot, Update
from telegram.error import BadRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def delete_command(bot: Bot, update: Update):
    message = update.message
    chat_id = message.chat_id
    command_message_id = message.message_id
    try:
        bot.delete_message(chat_id=chat_id, message_id=command_message_id)
    except BadRequest:
        logger.info("Command was already deleted %s", command_message_id)


def reply_to_message(bot, update, reply, disable_web_page_preview=True):
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
    delete_command(bot, update)

