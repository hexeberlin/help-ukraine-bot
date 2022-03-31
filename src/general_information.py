from typing import List

from telegram import Bot, Update, BotCommand
from telegram.ext import Dispatcher, CommandHandler

from src.common import guidebook, reply_to_message, get_param, delete_command, send_results
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


def germany_asyl_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/germany_asyl")
    delete_command(bot, update)
    results = guidebook.get_germany_asyl(name=name)
    reply_to_message(bot, update, results)


def germany_asyl_all_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.germany_asyl, name=None)


def telegram_translation_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.telegram_translation, name=None)

def register_commands(dispatcher: Dispatcher) -> List[BotCommand]:
    dispatcher.add_handler(CommandHandler("general_information", general_information_command))
    dispatcher.add_handler(CommandHandler("germany_asyl", germany_asyl_command))
    dispatcher.add_handler(CommandHandler("germany_asyl_all", germany_asyl_all_command))
    dispatcher.add_handler(CommandHandler("handbook", handbook))
    dispatcher.add_handler(CommandHandler("legal", legal_command))
    dispatcher.add_handler(CommandHandler("minors", minors_command))
    dispatcher.add_handler(CommandHandler("official_information", official_information_command))
    dispatcher.add_handler(CommandHandler("socialhelp", social_help_command))
    dispatcher.add_handler(CommandHandler("translators", translators_command))
    dispatcher.add_handler(CommandHandler("transport", transport_command))
    dispatcher.add_handler(CommandHandler("telegram_translation", telegram_translation_command))


    return [
        BotCommand("general_information", "General information"),
        BotCommand("germany_asyl", "Germany-wide refugee centers, you need to pass the name of the Bundesland"),
        BotCommand("germany_asyl_all", "Germany-wide refugee centers"),
        BotCommand("handbook", "FAQ"), BotCommand("legal", "Chat for legal help"),
        BotCommand("legal", "Chat for legal help"),
        BotCommand("minors", "Help for unaccompanied minors"),
        BotCommand("official_information", "Official information"),
        BotCommand("socialhelp", "Social help"),
        BotCommand("translators", "Translators"),
        BotCommand("transport", "transport"),
        BotCommand("telegram_translation", "Telegram Translation"),

    ]
