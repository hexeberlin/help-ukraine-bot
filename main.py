import logging

from telegram import Update, Bot
from telegram.utils.helpers import effective_message_type

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
# ALARM_TIME_SECONDS = 60*60
ALARM_TIME_SECONDS = 10

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

last_alarm_time = None


def help_command(bot: Bot, update: Update) -> None:
    """Send a message when the command /help is issued."""
    bot.send_message(chat_id=update.message.chat.id, text=REMINDER_MESSAGE)


def check_timer(bot: Bot, update: Update):
    """check_timer"""
    global last_alarm_time
    if last_alarm_time and (datetime.now() - last_alarm_time).seconds > ALARM_TIME_SECONDS:
        last_alarm_time = datetime.now()
        bot.send_message(chat_id=update.message.chat.id, text='Alarm')


def start_timer(bot: Bot, update: Update):
    """start_timer"""
    global last_alarm_time
    bot.send_message(chat_id=update.message.chat.id,
                     text='Starting!')
    last_alarm_time = datetime.now()


def stop_timer(bot: Bot, update: Update):
    """stop_timer"""
    global last_alarm_time
    bot.send_message(chat_id=update.message.chat.id,
                     text='Stoped!')
    last_alarm_time = None


def delete_greetings(bot: Bot, update: Update) -> None:
    """Echo the user message."""
    if effective_message_type(update.message) in ['new_chat_members', 'left_chat_member']:
        bot.delete_message(chat_id=update.message.chat.id,
                           message_id=update.message.message_id)


commands = {
    '//start': start_timer,
    '//stop': stop_timer,
    '//help': help_command
}


def webhook(request):
    """webhook"""
    bot = Bot(token=TOKEN)
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        logger.info(
            f'Got message {update.message.message_id} from chat {update.message.chat.id}')

        if update.message.text in commands:
            commands[update.message.text](bot, update)

        check_timer(bot, update)

        delete_greetings(bot, update)

    return "OK"
