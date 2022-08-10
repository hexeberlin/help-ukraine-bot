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


def berlinpass_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.berlinpass, name=None)


def beschwerde_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.beschwerde, name=None)


def kindergeld_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.kindergeld, name=None)


def leave_command(bot: Bot, update: Update):
    send_results(bot, update, group_name=NameType.leave, name=None)


def register_commands(dispatcher: Dispatcher) -> List[BotCommand]:
    dispatcher.add_handler(CommandHandler("berlinpass", berlinpass_command))
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
        BotCommand("berlinpass", "Как получить BerlinPass"),
        BotCommand("beschwerde", "Куда обратиться с жалобой"),
        BotCommand("euro_9", "Проездной за 9 евро"),
        BotCommand("general_information", "Официальная информация"),
        BotCommand("handbook", "Часто задаваемые вопросы"),
        BotCommand("kindergeld", "Как получить детское пособие (Kindergeld)"),
        BotCommand("legal", "Юридическая помощь"),
        BotCommand("leave", "Как сообщить JobCenter о временном отсутсвии"),
        BotCommand("minors", "Помощь для несовершеннолетних без сопровождения"),
        BotCommand("moving", "Сменить место первой регистрации"),
        BotCommand("no_ads", "Доски обьявлений и тематические чаты"),
        BotCommand("rundfunk", "Освобожение от налога на радио и ТВ"),
        BotCommand("socialhelp", "Социальная помощь"),
        BotCommand("translators", "Помощь переводчиков"),
        BotCommand("transport", "Транспорт"),
        BotCommand("telegram_translation", "Функция перевода в telegram"),
        BotCommand("wbs", "Что такое Wohnberechtigungsschein"),
    ]
