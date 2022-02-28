import logging

from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils.helpers import effective_message_type

import os

APP_NAME = os.environ.get("APP_NAME", "telegram-bot-help-in-berlin")
PORT = int(os.environ.get("PORT", 5000))
TOKEN = os.environ["TOKEN"]
REMINDER_MESSAGE = """
  Dear group members,
  We remind you that this is a group for helping and finding help. If you can – write in English. Please refrain from putting unrelated entries here. Anybody adding hate or trolling comments will be banned from the group.
  The overview of useful links  about documents, transport, accommodation etc. can be found here https://bit.ly/help-for-ukrainians

  Уважаемые участники группы,
  Напоминаем вам, что цель этой группы – предоставление и поиск помощи. Если можете – пожалуйста пишите по английски. Пожалуйста, воздержитесь от размещения здесь записей, не имеющих отношения к теме. Пользователи, добавляющие агрессивные или тролящие комментарии,  будут удаляны из группы.
  Обзор полезных ссылок о документах, транспорте, жилье и т.д. можно найти здесь
   https://bit.ly/help-for-ukrainians

  Шановні учасники групи
  Нагадуємо вам, що це група для допомоги та пошуку допомоги. Якщо можете – пишіть англійською. Будь ласка, утримайтеся від розміщення записів, що не мають відношення до теми. Будь-хто, хто додаватиме коментарі ненависті або тролінгу, буде видалено з групи.
  Огляд корисних посилань про документи, транспорт, житло тощо. можна знайти тут
   https://bit.ly/help-for-ukrainians
"""
REMINDER_INTERVAL = int(os.environ.get("REMINDER_INTERVAL", 30 * 60))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def help_command(bot: Bot, update: Update) -> None:
    """Send a message when the command /help is issued."""
    bot.send_message(chat_id=update.message.chat_id, text=REMINDER_MESSAGE)


def handle_msg(bot: Bot, update: Update) -> None:
    """Echo the user message."""
    tp = effective_message_type(update.message)
    logger.info(f"Handling type is {tp}")
    if effective_message_type(update.message) in [
        "new_chat_members",
        "left_chat_member",
    ]:
        bot.delete_message(
            chat_id=update.message.chat_id, message_id=update.message.message_id
        )


def callback_alarm(bot: Bot, job):
    """callback_alarm"""
    chat_id = job.context
    chat = bot.get_chat(chat_id)
    message = chat.pinned_message if chat.pinned_message else REMINDER_MESSAGE
    logger.info(f"Sending a reminder to chat {chat_id}")
    bot.send_message(chat_id=chat_id, text=message)


def callback_timer(bot: Bot, update: Update, job_queue):
    """callback_timer"""
    bot.send_message(chat_id=update.message.chat_id, text="Starting!")
    job_queue.run_repeating(
        callback_alarm, REMINDER_INTERVAL, first=1, context=update.message.chat_id
    )


def stop_timer(bot: Bot, update: Update, job_queue):
    """stop_timer"""
    bot.send_message(chat_id=update.message.chat_id, text="Stoped!")
    job_queue.stop()


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", callback_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("stop", stop_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.all, handle_msg))

    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook(f"https://{APP_NAME}.herokuapp.com/{TOKEN}")

    updater.idle()


if __name__ == "__main__":
    main()
