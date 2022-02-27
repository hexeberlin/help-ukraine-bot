import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import requests
import telegram
import os
from datetime import datetime
TOKEN = os.environ["TOKEN"]
REMINDER_MESSAGE = """
    Dear group members,
    We remind you that this is a group for helping and finding help. Please refrain from putting unrelated entries here. Anybody adding hate or trolling comments will be banned from the group.
    The overview of useful links  about documents, transport, accommodation etc. can be found here https://bit.ly/help-for-ukrainians

    Уважаемые участники группы,
    Напоминаем вам, что цель этой группы – предоставление и поиск помощи. Пожалуйста, воздержитесь от размещения здесь записей, не имеющих отношения к теме. Пользователи, добавляющие агрессивные или тролящие комментарии,  будут удаляны из группы.
    Обзор полезных ссылок о документах, транспорте, жилье и т.д. можно найти здесь
        https://bit.ly/help-for-ukrainians

    Шановні учасники групи
    Нагадуємо вам, що це група для допомоги та пошуку допомоги. Будь ласка, утримайтеся від розміщення записів, що не мають відношення до теми. Будь-хто, хто додаватиме коментарі ненависті або тролінгу, буде видалено з групи.
    Огляд корисних посилань про документи, транспорт, житло тощо. можна знайти тут
        https://bit.ly/help-for-ukrainians
"""

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text(REMINDER_MESSAGE)


def is_greeting(txt: str)->bool:
    return 

def handle_msg(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    if is_greeting('joined the group' in update.message.text or 'left the group' in update.message.text):
        update.message.delete()


def callback_alarm(bot, job):
    bot.send_message(chat_id=job.context, text='Alarm')

def callback_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id,
                      text='Starting!')
    job_queue.run_repeating(callback_alarm, 5, context=update.message.chat_id)

def stop_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id,
                      text='Stoped!')
    job_queue.stop()
    
def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler('start', callback_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler('stop', stop_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_msg))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    
if __name__ == '__main__':
    main()

