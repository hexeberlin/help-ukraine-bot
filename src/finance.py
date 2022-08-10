from typing import List

from telegram import Bot, Update, BotCommand
from telegram.ext import Dispatcher, CommandHandler

from src.common import send_results
from src.guidebook import NameType


def banking_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.banking, name=None)


def hryvnia_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.hryvnia, name=None)


def schufa_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.schufa, name=None)


def register_commands(dispatcher: Dispatcher) -> List[BotCommand]:
    dispatcher.add_handler(CommandHandler("banking", banking_command))
    dispatcher.add_handler(CommandHandler("hryvnia", hryvnia_command))
    dispatcher.add_handler(CommandHandler("schufa", schufa_command))

    return [
        BotCommand("banking", "Где открыть банковский счёт"),
        BotCommand("hryvnia", "Обменять гривны"),
        BotCommand("schufa", "Как получить справку Schufa"),
    ]
