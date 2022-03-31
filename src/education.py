from typing import List

from telegram import BotCommand, Bot, Update
from telegram.ext import Dispatcher, CommandHandler

from src.common import send_results
from src.guidebook import NameType


def children_lessons_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.education, name="Онлайн уроки для детей")


def deutsch_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.german, name=None)


def education_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.education, name=None)


def university_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.uni, name=None)


def register_commands(dispatcher: Dispatcher) -> List[BotCommand]:
    dispatcher.add_handler(CommandHandler("children_lessons", children_lessons_command))
    dispatcher.add_handler(CommandHandler("deutsch", deutsch_command))
    dispatcher.add_handler(CommandHandler("education", education_command))
    dispatcher.add_handler(CommandHandler("uni", university_command))

    return [
        BotCommand("children_lessons", "Online lessons for children from Ukraine"),
        BotCommand("deutsch", "German lessons"),
        BotCommand("education", "Overview of education in Germany"),
        BotCommand("uni", "Universities in Germany"),
    ]
