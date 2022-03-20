"""put module docstring here"""
import configparser
from os import environ as env
import logging
from functools import wraps
from typing import Tuple
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
from telegram.error import BadRequest
from telegram.utils.helpers import effective_message_type

import commands
from guidebook import Guidebook
from knowledge import search

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read("settings.env")

try:
    APP_NAME = env["APP_NAME"]
    TOKEN = env["TOKEN"]
except KeyError:
    APP_NAME = config.get("DEVELOPMENT", "APP_NAME")
    TOKEN = config.get("DEVELOPMENT", "TOKEN")

PORT = int(env.get("PORT", 5000))
REMINDER_MESSAGE = env.get("REMINDER_MESSAGE", "I WILL POST PINNED MESSAGE HERE")
REMINDER_INTERVAL_PINNED = int(env.get("REMINDER_INTERVAL", 30 * 60))
REMINDER_INTERVAL_INFO = int(env.get("REMINDER_INTERVAL", 10 * 60))
THUMB_URL = env.get(
    "THUMB_URL",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/2560px-Flag_of_Ukraine.svg.png",
)

BERLIN_HELPS_UKRAIN_CHAT_ID = [-1001589772550, -1001790676165, -735136184]
PINNED_JOB = "pinned"
SOCIAL_JOB = "social"
JOBS_NAME = [PINNED_JOB, SOCIAL_JOB]

guidebook = Guidebook()


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


def send_social_reminder(bot: Bot, job: Job):
    """send_reminder"""
    chat_id = job.context
    logger.info("Sending a social reminder to chat %s", chat_id)
    results = commands.social_help()
    bot.send_message(chat_id=chat_id, text=results, disable_web_page_preview=True)


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


@restricted
def start_timer(bot: Bot, update: Update, job_queue: JobQueue):
    """start_timer"""
    message = update.message
    chat_id = message.chat_id
    command_message_id = message.message_id
    if chat_id in BERLIN_HELPS_UKRAIN_CHAT_ID:
        reminder(bot, update, job_queue)
    try:
        bot.delete_message(chat_id=chat_id, message_id=command_message_id)
    except BadRequest:
        logger.info("Command was already deleted %s", command_message_id)


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


def find_replies(update: Update) -> None:
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


def reply_to_message(bot, update, reply, disable_web_page_preview=True):
    message = update.message
    chat_id = message.chat_id
    command_message_id = message.message_id

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
    try:
        bot.delete_message(chat_id=chat_id, message_id=command_message_id)
    except BadRequest:
        logger.info("Command was already deleted %s", command_message_id)


def get_param(bot, update, command):
    bot_name = bot.name
    return (
        update.message.text.removeprefix(command).replace(bot_name, "").strip().lower()
    )


def animal_help_command(bot: Bot, update: Update):
    results = guidebook.get_animal_help()
    reply_to_message(bot, update, results)


def children_lessons_command(bot: Bot, update: Update):
    results = commands.teachers_for_peace()
    reply_to_message(bot, update, results)


def cities_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/cities")
    results = guidebook.get_cities(name=name)
    reply_to_message(bot, update, results)


def cities_all_command(bot: Bot, update: Update):
    results = guidebook.get_cities_all()
    reply_to_message(bot, update, results)


def countries_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/countries")
    results = guidebook.get_countries(name=name)
    reply_to_message(bot, update, results)


def dentist_command(bot: Bot, update: Update):
    results = guidebook.get_dentist()
    reply_to_message(bot, update, results)


def deutsch_command(bot: Bot, update: Update):
    results = guidebook.get_german()
    reply_to_message(bot, update, results)


def evac_command(bot: Bot, update: Update):
    results = guidebook.get_evacuation()
    reply_to_message(bot, update, results)


def evac_cities_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/evacuation_cities")
    results = guidebook.get_evacuation_cities(name=name)
    reply_to_message(bot, update, results)


def freestuff_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/freestuff")
    results = guidebook.get_freestuff(name=name)
    reply_to_message(bot, update, results)


def germany_domestic_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/germany_domestic")
    results = guidebook.get_germany_domestic(name=name)
    reply_to_message(bot, update, results)


def handbook(bot: Bot, update: Update):
    results = commands.handbook()
    reply_to_message(bot, update, results)


def help_command(bot: Bot, update: Update):
    """Send a message when the command /help is issued."""
    results = commands.help()
    reply_to_message(bot, update, results)


def hryvnia_command(bot: Bot, update: Update):
    results = commands.hryvnia()
    reply_to_message(bot, update, results)


def humanitarian_aid_command(bot: Bot, update: Update):
    results = guidebook.get_humanitarian()
    reply_to_message(bot, update, results)


def jobs_command(bot: Bot, update: Update):
    results = guidebook.get_jobs()
    reply_to_message(bot, update, results)


def kids_with_special_needs_command(bot: Bot, update: Update):
    results = commands.kids_with_special_needs()
    reply_to_message(bot, update, results)


def legal_command(bot: Bot, update: Update):
    results = commands.legal()
    reply_to_message(bot, update, results)


def medical_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/medical")
    results = guidebook.get_medical(name=name)
    reply_to_message(bot, update, results)


def social_help_command(bot: Bot, update: Update):
    results = commands.social_help()
    reply_to_message(bot, update, results)


def taxi_command(bot: Bot, update: Update):
    results = guidebook.get_taxis()
    reply_to_message(bot, update, results)


def translators_command(bot: Bot, update: Update):
    results = commands.translators()
    reply_to_message(bot, update, results)


def travel_command(bot: Bot, update: Update):
    results = guidebook.get_travel()
    reply_to_message(bot, update, results)


def volunteer_command(bot: Bot, update: Update):
    results = guidebook.get_volunteer()
    reply_to_message(bot, update, results)


def show_command_list(bot: Bot):
    command_list = [
        BotCommand(
            "cities", "сhats for german cities, you need to pass the name of the city"
        ),
        BotCommand(
            "cities_all",
            "сhats for german cities, you need to pass the name of the city",
        ),
        BotCommand("children_lessons", "online lessons for children from Ukraine"),
        BotCommand("countries", "сhats for countries"),
        BotCommand("dentist", "dentist help"),
        BotCommand("deutsch", "german lessons"),
        BotCommand("evacuation", "general evacuation info"),
        BotCommand("evacuation_cities", "evacuation chats for ukrainian cities"),
        BotCommand("freestuff", "free stuff in berlin"),
        BotCommand("germany_domestic", "Germany-wide refugee centers"),
        BotCommand("handbook", "FAQ"),
        BotCommand("help", "bot functionality"),
        BotCommand("hryvnia", "Hryvnia exchange"),
        BotCommand("humanitarian", "Humanitarian aid"),
        BotCommand("jobs", "jobs in germany"),
        BotCommand("kids_with_special_needs", "help for children with special needs"),
        BotCommand("legal", "сhat for legal help"),
        BotCommand("medical", "medical help"),
        BotCommand("socialhelp", "social help"),
        BotCommand("taxis", "taxi service"),
        BotCommand("translators", "translators"),
        BotCommand("travel", "travel possibilities"),
        BotCommand("vet", "animal help"),
        BotCommand("volunteer", "volunteer"),
    ]
    bot.set_my_commands(command_list)


def add_commands(dispatcher):
    # Commands
    dispatcher.add_handler(CommandHandler("start", start_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("stop", stop_timer, pass_job_queue=True))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(CommandHandler("children_lessons", children_lessons_command))
    dispatcher.add_handler(CommandHandler("cities", cities_command))
    dispatcher.add_handler(CommandHandler("cities_all", cities_all_command))
    dispatcher.add_handler(CommandHandler("countries", countries_command))
    dispatcher.add_handler(CommandHandler("dentist", dentist_command))
    dispatcher.add_handler(CommandHandler("deutsch", deutsch_command))
    dispatcher.add_handler(CommandHandler("evacuation", evac_command))
    dispatcher.add_handler(CommandHandler("evacuation_cities", evac_cities_command))
    dispatcher.add_handler(CommandHandler("freestuff", freestuff_command))
    dispatcher.add_handler(CommandHandler("germany_domestic", germany_domestic_command))
    dispatcher.add_handler(CommandHandler("handbook", handbook))
    dispatcher.add_handler(CommandHandler("hryvnia", hryvnia_command))
    dispatcher.add_handler(CommandHandler("humanitarian", humanitarian_aid_command))
    dispatcher.add_handler(CommandHandler("jobs", jobs_command))
    dispatcher.add_handler(
        CommandHandler("kids_with_special_needs", kids_with_special_needs_command)
    )
    dispatcher.add_handler(CommandHandler("legal", legal_command))
    dispatcher.add_handler(CommandHandler("medical", medical_command))
    dispatcher.add_handler(CommandHandler("socialhelp", social_help_command))
    dispatcher.add_handler(CommandHandler("taxis", taxi_command))
    dispatcher.add_handler(CommandHandler("translators", translators_command))
    dispatcher.add_handler(CommandHandler("travel", travel_command))
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
