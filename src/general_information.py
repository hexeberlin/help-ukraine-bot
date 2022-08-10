from typing import List

from telegram import Bot, Update, BotCommand
from telegram.ext import Dispatcher, CommandHandler

from src.common import send_results
from src.guidebook import NameType


def translators_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.translators, name=None)


def transport_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.transport, name=None)


def social_help_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.social_help, name=None)


def minors_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.minors, name=None)


def official_information_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.statements, name=None)


def legal_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.legal, name=None)


def handbook(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.handbook, name=None)


def general_information_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.general_information, name=None)


def telegram_translation_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.telegram_translation, name=None)


def moving_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.moving, name=None)


def euro_9_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.euro_9, name=None)


def rundfunk_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.rundfunk, name=None)


def wbs_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.wbs, name=None)


def no_ads_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.no_ads, name=None)


def beschwerde_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.beschwerde, name=None)


def kindergeld_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.kindergeld, name=None)


def leave_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.leave, name=None)


def register_commands(dispatcher: Dispatcher) -> List[BotCommand]:
    dispatcher.add_handler(CommandHandler("beschwerde", beschwerde_command))
    dispatcher.add_handler(CommandHandler("euro_9", euro_9_command))
    dispatcher.add_handler(CommandHandler("general_information", general_information_command))
    dispatcher.add_handler(CommandHandler("handbook", handbook))
    dispatcher.add_handler(CommandHandler("kindergeld", kindergeld_command))
    dispatcher.add_handler(CommandHandler("leave", leave_command))
    dispatcher.add_handler(CommandHandler("legal", legal_command))
    dispatcher.add_handler(CommandHandler("minors", minors_command))
    dispatcher.add_handler(CommandHandler("moving", moving_command))
    dispatcher.add_handler(CommandHandler("no_ads", no_ads_command))
    dispatcher.add_handler(CommandHandler("official_information", official_information_command))
    dispatcher.add_handler(CommandHandler("rundfunk", rundfunk_command))
    dispatcher.add_handler(CommandHandler("socialhelp", social_help_command))
    dispatcher.add_handler(CommandHandler("translators", translators_command))
    dispatcher.add_handler(CommandHandler("transport", transport_command))
    dispatcher.add_handler(CommandHandler("telegram_translation", telegram_translation_command))
    dispatcher.add_handler(CommandHandler("wbs", wbs_command))

    return [
        BotCommand("beschwerde", "Where to file complains"),
        BotCommand("euro_9", "9 Euro Ticket"),
        BotCommand("general_information", "General information"),
        BotCommand("handbook", "FAQ"),
        BotCommand("kindergeld", "How to apply for children money (Kindergeld)"),
        BotCommand("legal", "Chat for legal help"),
        BotCommand("leave", "How to inform JobCenter about leaving"),
        BotCommand("minors", "Help for unaccompanied minors"),
        BotCommand("moving", "Moving from first registration"),
        BotCommand("no_ads", "Do not post advertisement in this group"),
        BotCommand("official_information", "Official information"),
        BotCommand("rundfunk", "Avoidance of TV and Radio fees"),
        BotCommand("socialhelp", "Social help"),
        BotCommand("translators", "Translators"),
        BotCommand("transport", "transport"),
        BotCommand("telegram_translation", "Telegram Translation"),
        BotCommand("wbs", "WBS - Wohnberechtigungsschein"),
    ]
