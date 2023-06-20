"""Module containing the bot commands."""

import logging
import os
from typing import List, Tuple

from schedule import Job
from telegram import (
    Bot,
    BotCommand,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
    ParseMode,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CommandHandler, JobQueue
from telegram.utils.helpers import effective_message_type

from src.common import (
    delete_command,
    format_knowledge_results,
    get_param,
    guidebook,
    parse_article,
    reply_to_message,
    restricted,
    send_results,
)
from src.config import (
    ADMIN_ONLY_CHAT_IDS,
    BERLIN_HELPS_UKRAINE_CHAT_ID,
    MONGO_BASE,
    MONGO_HOST,
    MONGO_PASS,
    MONGO_USER,
    PINNED_JOB,
    REMINDER_INTERVAL_INFO,
    REMINDER_INTERVAL_PINNED,
    REMINDER_MESSAGE,
    SOCIAL_JOB,
    THUMB_URL,
)
from src.guidebook import NameType
from src.mongo import connect
from src.services import Articles

db = connect(MONGO_HOST, MONGO_USER, MONGO_PASS, MONGO_BASE)
TEST_CHAT = "tests"
articles_service = Articles(db, TEST_CHAT)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
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

    for command in guidebook.guidebook.keys():
        if command in {"cities", "countries"}:
            continue

        def handler(bot: Bot, update: Update):
            send_results(bot, update, group_name=command)

        dispatcher.add_handler(CommandHandler(command, handler))

    # Those are special.
    dispatcher.add_handler(CommandHandler("cities", cities_command))
    dispatcher.add_handler(CommandHandler("countries", countries_command))
    dispatcher.add_handler(CommandHandler("cities_all", cities_all_command))
    dispatcher.add_handler(CommandHandler("countries_all", countries_all_command))

    # Articles
    dispatcher.add_handler(CommandHandler("add", add_article_command))
    dispatcher.add_handler(CommandHandler("list", list_articles_command))
    dispatcher.add_handler(CommandHandler("faq", get_article_command))
    dispatcher.add_handler(CommandHandler("delete", delete_article_command))

    all_commands = [
        BotCommand(command, description)
        for command, description in guidebook.descriptions.items()
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


@restricted
def add_article_command(bot: Bot, update: Update):
    article = parse_article(update.message, "/add", bot.name)
    if article:
        articles_service.add(article)
        reply_to_message(bot, update, "article added")
    else:
        reply_to_message(bot, update, "Invalid message format")


@restricted
def list_articles_command(bot: Bot, update: Update):
    articles = articles_service.list()
    keys_title = "".join([str(a) for a in articles])
    msg = f"**Available articles:**\n{keys_title}"
    reply_to_message(bot, update, msg)


@restricted
def get_article_command(bot: Bot, update: Update):
    key = get_param(bot, update, "/faq")
    article = articles_service.get(key)
    keys = "".join(article.keys)
    message = f"**keys:** {keys}\n{article.title}\n{article.content}"
    reply_to_message(bot, update, message)


@restricted
def delete_article_command(bot: Bot, update: Update):
    key = get_param(bot, update, "/delete")
    articles_service.delete(key)
    message = f"key {key} deleted"
    reply_to_message(bot, update, message)


def cities_all_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.cities, name=None)


def countries_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/countries")
    delete_command(bot, update)
    results = guidebook.get_countries(name=name)
    reply_to_message(bot, update, results)


def countries_all_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.countries, name=None)


def help_command(bot: Bot, update: Update):
    delete_command(bot, update)
    results = format_knowledge_results(help_text())
    reply_to_message(bot, update, results)


def cities_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/cities")
    delete_command(bot, update)
    results = guidebook.get_cities(name=name)
    reply_to_message(bot, update, results)


def search_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.search, name=None)


@restricted
def start_timer(bot: Bot, update: Update, job_queue: JobQueue):
    """start_timer"""
    message = update.message
    chat_id = message.chat_id
    command_message_id = message.message_id
    if chat_id in BERLIN_HELPS_UKRAINE_CHAT_ID:
        reminder(bot, update, job_queue)
    try:
        bot.delete_message(chat_id=chat_id, message_id=command_message_id)
    except BadRequest:
        logger.info("Command was already deleted %s", command_message_id)


@restricted
def admins_only(bot: Bot, update: Update):
    chat_id = update.message.chat_id
    ADMIN_ONLY_CHAT_IDS.append(chat_id)
    bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)


@restricted
def admins_only_revert(bot: Bot, update: Update):
    chat_id = update.message.chat_id
    ADMIN_ONLY_CHAT_IDS.remove(chat_id)
    bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)


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
    results = guidebook.get_results(group_name=NameType.social_help, name=None)
    bot.send_message(chat_id=chat_id, text=results, disable_web_page_preview=True)


def find_articles_command(update: Update) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    articles = articles_service.find(query)
    results = [
        InlineQueryResultArticle(
            id=a.id,
            title=a.title,
            input_message_content=InputTextMessageContent(
                str(a), parse_mode=ParseMode.MARKDOWN
            ),
            thumb_url=THUMB_URL,
        )
        for a in articles
    ]

    update.inline_query.answer(results)


def delete_greetings(bot: Bot, update: Update) -> None:
    """Echo the user message."""
    message = update.message
    if message:
        msg_type = effective_message_type(message)
        logger.debug("Handling type is %s", msg_type)
        if effective_message_type(message) in [
            "new_chat_members",
            "left_chat_member",
        ]:
            bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
