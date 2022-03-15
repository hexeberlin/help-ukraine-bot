"""put module docstring here"""
import configparser
from os import environ as env
import logging
import schedule
from functools import wraps

from telegram import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
    Update,
    Bot,
    BotCommand,
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
from telegram.utils.helpers import effective_message_type

import commands
import guidebook
from knowledge import search

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read('settings.env')

try:
    APP_NAME = env['APP_NAME']
    TOKEN = env['TOKEN']
except KeyError:
    APP_NAME = config.get('DEVELOPMENT', 'APP_NAME')
    TOKEN = config.get('DEVELOPMENT', 'TOKEN')
PORT = int(env.get("PORT", 5000))
REMINDER_MESSAGE = env.get("REMINDER_MESSAGE", "I WILL POST PINNED MESSAGE HERE")
REMINDER_INTERVAL_PINNED = int(env.get("REMINDER_INTERVAL", 30 * 60))
REMINDER_INTERVAL_INFO = int(env.get("REMINDER_INTERVAL", 5 * 60))
THUMB_URL = env.get(
    "THUMB_URL",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/2560px-Flag_of_Ukraine.svg.png",
)
BOOK = guidebook.load_guidebook()
BERLIN_HELPS_UKRAIN_CHAT_ID = [-1001589772550, -1001790676165, -735136184]


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


def send_pinned_reminder(bot: Bot, update: Update, chat_id: str):
    """send_reminder"""
    logger.info("Sending an info reminder to chat %s", chat_id)
    social_help_command(bot, update)


def send_info_reminder(bot: Bot, chat_id: str):
    """send_reminder"""
    chat = bot.get_chat(chat_id)
    msg: Message = chat.pinned_message
    logger.info("Sending a info to chat %s", chat_id)

    if msg:
        bot.forward_message(chat_id, chat_id, msg.message_id)
    else:
        bot.send_message(chat_id=chat_id, text=REMINDER_MESSAGE)


def delete_greetings(bot: Bot, update: Update) -> None:
    """Echo the user message."""
    if update.message is not None:
        msg_type = effective_message_type(update.message)
        logger.debug("Handling type is %s", msg_type)
        if effective_message_type(update.message) in [
            "new_chat_members",
            "left_chat_member",
        ]:
            bot.delete_message(
                chat_id=update.message.chat_id, message_id=update.message.message_id
            )


@restricted
def start_timer(bot: Bot, update: Update, job_queue: JobQueue):
    """start_timer"""
    chat_id = update.message.chat_id
    command_message_id = update.message.message_id
    if chat_id in BERLIN_HELPS_UKRAIN_CHAT_ID:
        reminder(bot, update, job_queue)

    bot.delete_message(chat_id=chat_id, message_id=command_message_id)


def reminder(bot: Bot, update: Update, job_queue: JobQueue):
    chat_id = update.message.chat_id
    logger.info("Started reminders in channel %s", chat_id)

    jobs: tuple[Job] = job_queue.get_jobs_by_name(chat_id)

    #  Restart already existing jobs
    for job in jobs:
        if not job.enabled:
            print("jan name: " + job.name)
            bot.send_message(
                chat_id=chat_id,
                text=f"I'm re-starting sending the reminders every {REMINDER_INTERVAL_PINNED}s.",
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text=f"I'm already sending the reminders every {REMINDER_INTERVAL_PINNED}s.",
            )
        job.enabled = True

    # Start a new job if there was none previously
    if not jobs:
        add_pinned_reminder_job(bot, update, job_queue)
        add_info_job(bot, update, job_queue)


def add_pinned_reminder_job(bot: Bot, update: Update, job_queue: JobQueue ):
    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text=f"I'm starting sending the reminders every {REMINDER_INTERVAL_PINNED}s.",
    )
    job_queue.run_repeating(
        send_info_reminder(bot, chat_id=chat_id), REMINDER_INTERVAL_PINNED, first=1, context=chat_id, name=chat_id
    )


def add_info_job(bot: Bot, update: Update, job_queue: JobQueue):
    chat_id = update.message.chat_id
    bot.send_message(
        chat_id=chat_id,
        text=f"I'm starting sending the reminders every {REMINDER_INTERVAL_INFO}s.",
    )
    job_queue.run_repeating(
        send_pinned_reminder(bot, update, chat_id=chat_id), REMINDER_INTERVAL_INFO, first=1, context=chat_id,
        name=chat_id
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


def reply_to_message(bot, update, reply):
    chat_id = update.message.chat_id
    command_message_id = update.message.message_id

    if update.message.reply_to_message is None:
        bot.send_message(chat_id=chat_id, text=reply)
    else:
        parent_message_id = update.message.reply_to_message.message_id
        bot.send_message(chat_id=chat_id, reply_to_message_id=parent_message_id, text=reply)

    bot.delete_message(chat_id=chat_id, message_id=command_message_id)


def get_param(bot, update, command):
    bot_name = bot.name
    return update.message.text.removeprefix(command).replace(bot_name, "").strip().lower()


def help_command(bot: Bot, update: Update):
    """Send a message when the command /help is issued."""
    help = commands.help()
    reply_to_message(bot, update, help)


def cities_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/cities")
    if name is None or not name:
        results = "Пожалуйста, уточните название города: /cities Name"
    else:
        results = commands.cities(BOOK, name)
    reply_to_message(bot, update, results)


def cities_all_command(bot: Bot, update: Update):
    results = commands.cities(BOOK)
    reply_to_message(bot, update, results)


def countries_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/countries")
    results = commands.countries(BOOK, name)
    reply_to_message(bot, update, results)


def hryvnia_command(bot: Bot, update: Update):
    results = commands.hryvnia()
    reply_to_message(bot, update, results)


def legal_command(bot: Bot, update: Update):
    results = commands.legal()
    reply_to_message(bot, update, results)


def children_lessons(bot: Bot, update: Update):
    results = commands.teachers_for_peace()
    reply_to_message(bot, update, results)


def handbook(bot: Bot, update: Update):
    results = commands.handbook()
    reply_to_message(bot, update, results)


def evac_command(bot: Bot, update: Update):
    results = commands.evacuation(BOOK)
    reply_to_message(bot, update, results)


def evac_cities_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/evacuation_cities")
    results = commands.evacuation_cities(BOOK, name)
    reply_to_message(bot, update, results)


def taxi_command(bot: Bot, update: Update):
    results = commands.taxis(BOOK)
    reply_to_message(bot, update, results)


def medical_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/medical")
    results = commands.medical(BOOK, name)
    reply_to_message(bot, update, results)


def dentist_command(bot: Bot, update: Update):
    results = commands.dentist(BOOK)
    reply_to_message(bot, update, results)


def social_help_command(bot: Bot, update: Update):
    results = commands.social_help()
    reply_to_message(bot, update, results)


def jobs_command(bot: Bot, update: Update):
    results = commands.jobs(BOOK)
    reply_to_message(bot, update, results)


def freestuff_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/freestuff")
    results = commands.freestuff(BOOK, name)
    reply_to_message(bot, update, results)


def animal_help_command(bot: Bot, update: Update):
    results = commands.animal_help(BOOK)
    reply_to_message(bot, update, results)


def volunteer_command(bot: Bot, update: Update):
    results = commands.volunteer(BOOK)
    reply_to_message(bot, update, results)


def show_command_list(bot: Bot):
    commands = [
        BotCommand("children_lessons", "online lessons for children from Ukraine"),
        BotCommand("cities", "сhats for german cities, you need to pass the name of the city"),
        BotCommand("cities_all", "сhats for german cities, you need to pass the name of the city"),
        BotCommand("countries", "сhats for countries"),
        BotCommand("evacuation", "general evacuation info"),
        BotCommand("evacuation_cities", "evacuation chats for ukrainian cities"),
        BotCommand("handbook", "FAQ"),
        BotCommand("help", "bot functionality"),
        BotCommand("hryvnia", "Hryvnia exchange"),
        BotCommand("legal", "сhat for legal help"),
        BotCommand("taxis", "сhat for legal help"),
        BotCommand("medical", "medical help"),
        BotCommand("dentist", "dentist help"),
        BotCommand("socialhelp", "social help"),
        BotCommand("jobs", "jobs in germany"),
        BotCommand("freestuff", "free stuff in berlin"),
        BotCommand("vet", "animal help"),
        BotCommand("volunteer", "volunteer"),

    ]
    bot.set_my_commands(commands)


def add_commands(dispatcher):
    # Commands
    dispatcher.add_handler(CommandHandler("start", start_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("stop", stop_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(CommandHandler("children_lessons", children_lessons))

    dispatcher.add_handler(CommandHandler("cities", cities_command))
    dispatcher.add_handler(CommandHandler("cities_all", cities_all_command))
    dispatcher.add_handler(CommandHandler("countries", countries_command))

    dispatcher.add_handler(CommandHandler("evacuation", evac_command))
    dispatcher.add_handler(CommandHandler("evacuation_cities", evac_cities_command))

    dispatcher.add_handler(CommandHandler("hryvnia", hryvnia_command))
    dispatcher.add_handler(CommandHandler("handbook", handbook))
    dispatcher.add_handler(CommandHandler("legal", legal_command))
    dispatcher.add_handler(CommandHandler("taxis", taxi_command))

    dispatcher.add_handler(CommandHandler("medical", medical_command))
    dispatcher.add_handler(CommandHandler("dentist", dentist_command))
    dispatcher.add_handler(CommandHandler("socialhelp", social_help_command))
    dispatcher.add_handler(CommandHandler("jobs", jobs_command))

    dispatcher.add_handler(CommandHandler("freestuff", freestuff_command))
    dispatcher.add_handler(CommandHandler("vet", animal_help_command))
    dispatcher.add_handler(CommandHandler("volunteer", volunteer_command))


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    add_commands(dispatcher)
    show_command_list(updater.bot)

    # Messages
    dispatcher.add_handler(MessageHandler(Filters.all, delete_greetings))

    # Inlines
    dispatcher.add_handler(InlineQueryHandler(find_replies))

    if APP_NAME == "TESTING":
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
        updater.bot.setWebhook(f"https://{APP_NAME}.herokuapp.com/{TOKEN}")

    updater.idle()


if __name__ == "__main__":
    main()
