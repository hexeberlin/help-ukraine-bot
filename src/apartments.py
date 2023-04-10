from typing import List

from telegram import Bot, Update, BotCommand
from telegram.ext import Dispatcher, CommandHandler

from src.common import send_results
from src.guidebook import NameType


def accommodation_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.accommodation, name=None)


def apartments_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.apartments, name=None)


def apartment_approval_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.apartment_approval, name=None)


def register_commands(dispatcher: Dispatcher) -> List[BotCommand]:
    dispatcher.add_handler(CommandHandler("accommodation", accommodation_command))
    dispatcher.add_handler(CommandHandler("apartments", apartments_command))
    dispatcher.add_handler(CommandHandler("apartment_approval", apartment_approval_command))
    return [
        BotCommand("accommodation", "Поиск временного жилья"),
        BotCommand("apartments", "Поиск постоянного жилья"),
        BotCommand("apartment_approval", "Процесс одобрения квартиры Jobcenter"),
    ]
