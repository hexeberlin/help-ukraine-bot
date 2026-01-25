"""Module containing the bot commands."""

import logging
import os
from typing import List, Tuple

from schedule import Job
from telegram import (
    Bot,
    BotCommand,
    Message,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CommandHandler, JobQueue
from telegram.utils.helpers import effective_message_type

from src.common import (
    delete_command,
    get_param,
    guidebook,
    reply_to_message,
    restricted,
    send_results,
)
from src.config import (
    ADMIN_ONLY_CHAT_IDS,
    BERLIN_HELPS_UKRAINE_CHAT_ID,
    PINNED_JOB,
    REMINDER_INTERVAL_INFO,
    REMINDER_INTERVAL_PINNED,
    REMINDER_MESSAGE,
    SOCIAL_JOB,
)
from src.guidebook import Guidebook

logger = logging.getLogger(__name__)


def help_text():
    return (
        "Привет! 🤖 "
        + os.linesep
        + "Я бот для помощи беженцам из Украины 🇺🇦 в Германии. "
        + os.linesep
        + "Большинство моих знаний относятся к Берлину, но есть и общая "
        + "полезная информация. Чтобы увидеть список поддерживаемых команд, "
        + "введите символ '/'. "
        + "\n\n"
        + "Если добавите меня в свой чат, не забудьте дать мне права "
        + "админа, пожалуйста, чтобы я мог удалять ненужные сообщения с "
        + "вызванными командами."
        + "\n\n\n"
        + "Вітання! 🤖 "
        + os.linesep
        + "Я бот для допомоги біженцям з України 🇺🇦 в Німеччині."
        + os.linesep
        + "Більшість моїх знань стосуються Берліну, але є й загальна "
        + "корисна інформація. Щоб побачити список команд, що підтримуються, "
        + "введіть символ '/'. "
        + "\n\n"
        + "Якщо додасте мене до свого чату, будь ласка, не забудьте надати "
        + "мені права адміна, щоб я зміг видаляти непотрібні повідомлення із "
        + "викликаними командами."
        + "\n\n\n"
        + "Hi! 🤖"
        + os.linesep
        + "I'm a bot helping refugees from Ukraine 🇺🇦 in Germany. "
        + os.linesep
        + "Most of my knowledge focuses on Berlin, but I have some "
        + "general useful information too. Type '/' to see the list of my "
        + "available commands."
        + "\n\n"
        + "If you add me to your chat, don't forget to grant me admin "
        + "rights, so that I can delete log messages and keep your chat clean."
    )


def add_commands(dispatcher) -> List[BotCommand]:
    # Commands
    dispatcher.add_handler(CommandHandler("start", start_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("stop", stop_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(CommandHandler("adminsonly", admins_only))
    dispatcher.add_handler(CommandHandler("adminsonly_revert", admins_only_revert))

    def build_handler(command: str):
        def handler(bot: Bot, update: Update):
            send_results(bot, update, group_name=command)

        return handler

    for command in guidebook.guidebook.keys():
        # Those are special.
        if command not in {"cities", "countries"}:
            dispatcher.add_handler(CommandHandler(command, build_handler(command)))

    # Those are special.
    dispatcher.add_handler(CommandHandler("cities", cities_command))
    dispatcher.add_handler(CommandHandler("countries", countries_command))
    dispatcher.add_handler(CommandHandler("cities_all", cities_all_command))
    dispatcher.add_handler(CommandHandler("countries_all", countries_all_command))

    all_commands = [
        BotCommand(command, description)
        for command, description in guidebook.descriptions.items()
        # Those are special.
        if command not in {"cities", "countries"}
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
    ]

    return all_commands


def cities_all_command(bot: Bot, update: Update):
    send_results(bot, update, group_name="cities", name=None)


def countries_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/countries")
    results = guidebook.get_countries(name=name)
    reply_to_message(bot, update, results)


def countries_all_command(bot: Bot, update: Update):
    send_results(bot, update, group_name="countries", name=None)


def help_command(bot: Bot, update: Update):
    results = Guidebook.format_results(help_text())
    reply_to_message(bot, update, results)


def cities_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/cities")
    results = guidebook.get_cities(name=name)
    reply_to_message(bot, update, results)


@restricted
def start_timer(bot: Bot, update: Update, job_queue: JobQueue):
    """start_timer"""
    message = update.message
    chat_id = message.chat_id
    if chat_id in BERLIN_HELPS_UKRAINE_CHAT_ID:
        reminder(bot, update, job_queue)
    delete_command(bot, update)


@restricted
def admins_only(bot: Bot, update: Update):
    chat_id = update.message.chat_id
    ADMIN_ONLY_CHAT_IDS.append(chat_id)
    delete_command(bot, update)


@restricted
def admins_only_revert(bot: Bot, update: Update):
    chat_id = update.message.chat_id
    ADMIN_ONLY_CHAT_IDS.remove(chat_id)
    delete_command(bot, update)


def reminder(bot: Bot, update: Update, job_queue: JobQueue):
    chat_id = update.message.chat_id
    logger.info("Started reminders in channel %s", chat_id)

    jobs: Tuple[Job] = job_queue.get_jobs_by_name(
        PINNED_JOB
    ) + job_queue.get_jobs_by_name(SOCIAL_JOB)

    #  Restart already existing jobs
    for job in jobs:
        if not job.enabled:
            job.enabled = True

    # Start a new job if there was none previously
    if not jobs:
        add_pinned_reminder_job(bot, update, job_queue)
        add_info_job(bot, update, job_queue)


def add_pinned_reminder_job(bot: Bot, update: Update, job_queue: JobQueue):
    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text=f"I'm starting sending the pinned reminder every {REMINDER_INTERVAL_PINNED}s.",
    )
    job_queue.run_repeating(
        send_pinned_reminder,
        REMINDER_INTERVAL_PINNED,
        first=1,
        context=chat_id,
        name=PINNED_JOB,
    )


def add_info_job(bot: Bot, update: Update, job_queue: JobQueue):
    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text=f"I'm starting sending the info reminder every {REMINDER_INTERVAL_INFO}s.",
    )
    job_queue.run_repeating(
        send_social_reminder,
        REMINDER_INTERVAL_INFO,
        first=1,
        context=chat_id,
        name=SOCIAL_JOB,
    )


@restricted
def stop_timer(bot: Bot, update: Update, job_queue: JobQueue):
    """stop_timer"""
    chat_id = update.message.chat_id

    #  Stop already existing jobs
    jobs: Tuple[Job] = job_queue.get_jobs_by_name(chat_id)
    for job in jobs:
        bot.send_message(chat_id=chat_id, text="I'm stopping sending the reminders.")
        job.enabled = False

    logger.info("Stopped reminders in channel %s", chat_id)


def send_pinned_reminder(bot: Bot, job: Job):
    """send_reminder"""
    chat_id = job.context
    chat = bot.get_chat(chat_id)
    msg: Message = chat.pinned_message
    logger.info("Sending pinned message to chat %s", chat_id)

    if msg:
        bot.forward_message(chat_id, chat_id, msg.message_id)
    else:
        bot.send_message(chat_id=chat_id, text=REMINDER_MESSAGE)


def send_social_reminder(bot: Bot, job: Job):
    """send_reminder"""
    chat_id = job.context
    logger.info("Sending a social reminder to chat %s", chat_id)
    results = guidebook.get_results(group_name="social_help", name=None)
    bot.send_message(chat_id=chat_id, text=results, disable_web_page_preview=True)


def delete_greetings(bot: Bot, update: Update) -> None:
    """Echo the user message."""
    message = update.message
    if message:
        msg_type = effective_message_type(message)
        logger.debug("Handling type is %s", msg_type)
        if msg_type in [
            "new_chat_members",
            "left_chat_member",
        ]:
            delete_command(bot, update)
