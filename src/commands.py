"""Module containing the bot commands."""

import logging
import os
from typing import List, Optional

from telegram import BotCommand, Message, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    Job,
    JobQueue,
)
from telegram.helpers import effective_message_type

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


def _job_name(job_type: str, chat_id: int) -> str:
    return f"{job_type}-{chat_id}"


def _chat_jobs(job_queue: Optional[JobQueue], chat_id: int) -> List[Job]:
    if job_queue is None:
        return []
    jobs: List[Job] = []
    for job_type in (PINNED_JOB, SOCIAL_JOB):
        jobs.extend(job_queue.get_jobs_by_name(_job_name(job_type, chat_id)))
    return jobs


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


def register(application: Application) -> List[BotCommand]:
    # Commands
    application.add_handler(CommandHandler("start", start_timer))
    application.add_handler(CommandHandler("stop", stop_timer))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("adminsonly", admins_only))
    application.add_handler(CommandHandler("adminsonly_revert", admins_only_revert))

    def build_handler(command: str):
        async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await send_results(update, context, group_name=command)

        return handler

    for command in guidebook.guidebook.keys():
        # Those are special.
        if command not in {"cities", "countries"}:
            application.add_handler(CommandHandler(command, build_handler(command)))

    # Those are special.
    application.add_handler(CommandHandler("cities", cities_command))
    application.add_handler(CommandHandler("countries", countries_command))
    application.add_handler(CommandHandler("cities_all", cities_all_command))
    application.add_handler(CommandHandler("countries_all", countries_all_command))

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


async def cities_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_results(update, context, group_name="cities", name=None)


async def countries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = get_param(update, "/countries")
    results = guidebook.get_countries(name=name)
    await reply_to_message(update, context, results)


async def countries_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_results(update, context, group_name="countries", name=None)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = Guidebook.format_results(help_text())
    await reply_to_message(update, context, results)


async def cities_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = get_param(update, "/cities")
    results = guidebook.get_cities(name=name)
    await reply_to_message(update, context, results)


@restricted
async def start_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """start_timer"""
    message = update.effective_message
    if not message:
        return
    chat_id = message.chat_id
    if chat_id in BERLIN_HELPS_UKRAINE_CHAT_ID:
        await reminder(update, context)
    await delete_command(update, context)


@restricted
async def admins_only(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat:
        return
    chat_id = chat.id
    ADMIN_ONLY_CHAT_IDS.append(chat_id)
    await delete_command(update, context)


@restricted
async def admins_only_revert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat:
        return
    chat_id = chat.id
    if chat_id in ADMIN_ONLY_CHAT_IDS:
        ADMIN_ONLY_CHAT_IDS.remove(chat_id)
    await delete_command(update, context)


async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return
    chat_id = message.chat_id
    job_queue = context.job_queue
    if job_queue is None:
        logger.warning("Job queue not configured; reminders cannot be scheduled.")
        return

    logger.info("Started reminders in channel %s", chat_id)

    jobs = _chat_jobs(job_queue, chat_id)

    # Restart already existing jobs
    for job in jobs:
        if not job.enabled:
            job.enabled = True

    # Start a new job if there was none previously
    if not jobs:
        await add_pinned_reminder_job(context, chat_id)
        await add_info_job(context, chat_id)


async def add_pinned_reminder_job(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"I'm starting sending the pinned reminder every {REMINDER_INTERVAL_PINNED}s.",
    )
    job_queue = context.job_queue
    if job_queue is None:
        return
    job_queue.run_repeating(
        send_pinned_reminder,
        interval=REMINDER_INTERVAL_PINNED,
        first=1,
        chat_id=chat_id,
        name=_job_name(PINNED_JOB, chat_id),
        data={"chat_id": chat_id},
    )


async def add_info_job(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"I'm starting sending the info reminder every {REMINDER_INTERVAL_INFO}s.",
    )
    job_queue = context.job_queue
    if job_queue is None:
        return
    job_queue.run_repeating(
        send_social_reminder,
        interval=REMINDER_INTERVAL_INFO,
        first=1,
        chat_id=chat_id,
        name=_job_name(SOCIAL_JOB, chat_id),
        data={"chat_id": chat_id},
    )


@restricted
async def stop_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """stop_timer"""
    chat = update.effective_chat
    if not chat:
        return
    chat_id = chat.id
    job_queue = context.job_queue
    if job_queue is None:
        logger.warning("Job queue not configured; cannot stop reminders.")
        return

    jobs = _chat_jobs(job_queue, chat_id)

    if jobs:
        await context.bot.send_message(
            chat_id=chat_id, text="I'm stopping sending the reminders."
        )

    # Stop already existing jobs
    for job in jobs:
        job.enabled = False

    logger.info("Stopped reminders in channel %s", chat_id)


async def send_pinned_reminder(context: ContextTypes.DEFAULT_TYPE):
    """send_reminder"""
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
        await context.bot.send_message(chat_id=chat_id, text=REMINDER_MESSAGE)


async def send_social_reminder(context: ContextTypes.DEFAULT_TYPE):
    """send_reminder"""
    job = context.job
    if job is None:
        return
    chat_id = job.chat_id
    logger.info("Sending a social reminder to chat %s", chat_id)
    results = guidebook.get_results(group_name="social_help", name=None)
    await context.bot.send_message(
        chat_id=chat_id, text=results, disable_web_page_preview=True
    )


async def delete_greetings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete join/left notifications to keep chats tidy."""
    message = update.effective_message
    if message:
        msg_type = effective_message_type(message)
        logger.debug("Handling type is %s", msg_type)
        if msg_type in [
            "new_chat_members",
            "left_chat_member",
        ]:
            await delete_command(update, context)
