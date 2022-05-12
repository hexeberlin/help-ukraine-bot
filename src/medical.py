from typing import List

from telegram import Bot, Update, BotCommand
from telegram.ext import Dispatcher, CommandHandler

from src.common import get_param, send_results
from src.guidebook import NameType


def dentist_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.dentist, name=None)


def medical_command(bot: Bot, update: Update):
    name = get_param(bot, update, "/medical")
    send_results(bot, update, group_name=NameType.medical, name=name)


def psychological_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.psychological, name=None)


def kids_with_special_needs_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.disabled, name="Помощь для детей с особыми потребностями")


def disabled_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.disabled, name=None)


def pregnant_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.pregnant, name=None)


def register_commands(dispatcher: Dispatcher) -> List[BotCommand]:
    dispatcher.add_handler(
        CommandHandler("kids_with_special_needs", kids_with_special_needs_command)
    )
    dispatcher.add_handler(CommandHandler("dentist", dentist_command))
    dispatcher.add_handler(CommandHandler("medical", medical_command))
    dispatcher.add_handler(CommandHandler("psychological", psychological_command))
    dispatcher.add_handler(CommandHandler("disabled", disabled_command))
    dispatcher.add_handler(CommandHandler("pregnant", pregnant_command))

    return [BotCommand("medical", "Medical help"),
            BotCommand("psychological", "Psychological help"),
            BotCommand("dentist", "Dentist help"),
            BotCommand("kids_with_special_needs", "Help for children with special needs"),
            BotCommand("disabled", "Disabled people"),
            BotCommand("pregnant", "Pregnant"),
            ]
