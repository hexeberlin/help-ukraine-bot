from typing import List

from telegram import Bot, Update, BotCommand
from telegram.ext import Dispatcher, CommandHandler

from src.common import send_results
from src.guidebook import NameType


def hryvnia_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.hryvnia, name=None)


def schufa_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.schufa, name=None)
    

def job_center_calc_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.job_center_calc, name=None)


def register_commands(dispatcher: Dispatcher) -> List[BotCommand]:
    dispatcher.add_handler(CommandHandler("hryvnia", hryvnia_command))
    dispatcher.add_handler(CommandHandler("job_center_calc", job_center_calc_command))
    dispatcher.add_handler(CommandHandler("schufa", schufa_command))

    return [
        BotCommand("hryvnia", "Обменять гривны"),
        BotCommand("job_center_calc", "Расчёт пособия от JobCenter при наличии зарплаты"),
        BotCommand("schufa", "Как получить справку Schufa"),
    ]
