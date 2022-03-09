"""put module docstring here"""
import os
import logging
from functools import wraps
from uuid import uuid4

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
    Update,
    Bot,
    ParseMode,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    InlineQueryHandler,
    Filters,
    CallbackContext,
    JobQueue,
    Job,
)
from telegram.utils.helpers import effective_message_type, escape_markdown

import commands
import guidebook
from knowledge import search

APP_NAME = os.environ["APP_NAME"]
PORT = int(os.environ.get("PORT", 5000))
TOKEN = os.environ["TOKEN"]
REMINDER_MESSAGE = os.environ.get("REMINDER_MESSAGE", "I WILL POST PINNED MESSAGE HERE")
SIREN_MESSAGE = "СИРЕНЫ"
REMINDER_INTERVAL = int(os.environ.get("REMINDER_INTERVAL", 30 * 60))
THUMB_URL = os.environ.get(
    "THUMB_URL",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/2560px-Flag_of_Ukraine.svg.png",
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


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


def send_reminder(bot: Bot, chat_id: str):
    """send_reminder"""
    chat = bot.get_chat(chat_id)
    msg: Message = chat.pinned_message
    logger.info("Sending a reminder to chat %s", chat_id)

    if msg:
        bot.forward_message(chat_id, chat_id, msg.message_id)
    else:
        bot.send_message(chat_id=chat_id, text=REMINDER_MESSAGE)

    # bot.send_message(chat_id=chat_id, text=SIREN_MESSAGE)


def help_command(bot: Bot, update: Update) -> None:
    """Send a message when the command /help is issued."""
    send_reminder(bot, chat_id=update.message.chat_id)


def delete_greetings(bot: Bot, update: Update) -> None:
    """Echo the user message."""
    msg_type = effective_message_type(update.message)
    logger.debug("Handling type is %s", msg_type)
    if effective_message_type(update.message) in [
        "new_chat_members",
        "left_chat_member",
    ]:
        bot.delete_message(
            chat_id=update.message.chat_id, message_id=update.message.message_id
        )


def alarm(bot: Bot, job: Job):
    """alarm"""
    chat_id = job.context
    send_reminder(bot, chat_id=chat_id)


@restricted
def start_timer(bot: Bot, update: Update, job_queue: JobQueue):
    """start_timer"""
    chat_id = update.message.chat_id
    logger.info("Started reminders in channel %s", chat_id)

    jobs: tuple[Job] = job_queue.get_jobs_by_name(chat_id)

    #  Restart already existing jobs
    for job in jobs:
        if not job.enabled:
            bot.send_message(
                chat_id=chat_id,
                text=f"I'm re-starting sending the reminders every {REMINDER_INTERVAL}s.",
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text=f"I'm already sending the reminders every {REMINDER_INTERVAL}s.",
            )
        job.enabled = True

    # Start a new job if there was none previously
    if not jobs:
        bot.send_message(
            chat_id=chat_id,
            text=f"I'm starting sending the reminders every {REMINDER_INTERVAL}s.",
        )
        job_queue.run_repeating(
            alarm, REMINDER_INTERVAL, first=1, context=chat_id, name=chat_id
        )


@restricted
def stop_timer(bot: Bot, update: Update, job_queue: JobQueue):
    """stop_timer"""
    chat_id = update.message.chat_id

    #  Stop already existing jobs
    jobs: tuple[Job] = job_queue.get_jobs_by_name(chat_id)
    for job in jobs:
        bot.send_message(chat_id=chat_id, text="I'm stopping sending the reminders.")
        job.enabled = False

    logger.info("Stopped reminders in channel %s", chat_id)


def find_replies(bot: Bot, update: Update) -> None:
    """Handle the inline query."""
    query = update.inline_query.query

    replies = search(query)
    results = [
        InlineQueryResultArticle(
            id=r.id,
            title=r.title,
            input_message_content=InputTextMessageContent(
                r.content, parse_mode=ParseMode.MARKDOWN
            ),
            thumb_url=THUMB_URL,
        )
        for r in replies
    ]

    update.inline_query.answer(results)


def cities_command(bot: Bot, update: Update, name=None):
    logger.info("cities")

    # book = guidebook.load_guidebook()
    # results = commands.cities(book, name)
    results = "heloo world"
    bot.send_message(chat_id=update.message.chat_id, text=results)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # book = guidebook.load_guidebook()

    # Commands
    dispatcher.add_handler(CommandHandler("start", start_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("stop", stop_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # dispatcher.add_handler(CommandHandler("cities", cities_command))

    # Messages
    dispatcher.add_handler(MessageHandler(Filters.all, delete_greetings))

    # Inlines
    dispatcher.add_handler(InlineQueryHandler(find_replies))

    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    updater.bot.setWebhook(f"https://{APP_NAME}.herokuapp.com/{TOKEN}")

    updater.idle()


if __name__ == "__main__":
    main()
