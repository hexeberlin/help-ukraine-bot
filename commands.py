import os

import guidebook
import knowledge

HRYVNIA_TITLE = "Обмен гривен/Exchange hryvnia"
LEGAL_TITLE = "Юридическая помощь/Legal help"
TEACHERS_TITLE = "Онлайн уроки для детей/Online lessons for children"
HANDBOOK_TITLE = "Mетодичка"
SOCIAL_HELP_TITLE = "Социальная помощь"
TRANSLATORS_TITLE = "Переводчики/Translators"
KIDS_WITH_SPECIAL_NEEDS_TITLE = "Дети с особыми образовательными потребностями/Kids with special needs"


def get_from_knowledge(title):
    replies = knowledge.replies
    return [p for p in replies if p.title == title][0].content


def animal_help(book, name=None):
    return guidebook.get_info(book, "animals", name)


def cities(book, name=None):
    return guidebook.get_info(book, "cities", name)


def countries(book, name=None):
    return guidebook.get_info(book, "countries", name)


def dentist(book, name=None):
    return guidebook.get_info(book, "dentist", name)


def deutsch(book, name=None):
     return guidebook.get_info(book, "deutsch", name)


def evacuation(book):
    return guidebook.evacuation(book)


def evacuation_cities(book, name=None):
    return guidebook.get_info(book, "evacuation_cities", name)


def freestuff(book, name=None):
    return guidebook.get_info(book, "freestuff", name)


def germany_domestic(book, name=None):
    separator = "=" * 30
    results = guidebook.germany_domestic(book, group_name="germany_domestic", name=name)
    return separator + "\n" + results + "\n" + separator


def handbook():
    return get_from_knowledge(HANDBOOK_TITLE)


def help():
    return (
        "Привет! Используйте одну из команд:\n"
        + "/cities чтобы увидеть чат помощи по городам Германии, вам нужно написать название города: /cities name\n"
        + "/cities_all чтобы увидеть все чаты помощи по городам Германии\n"
        + "/countries чтобы увидеть все чаты помощи по странам\n"
        + "/hryvnia чтобы получить информацию про обмен гривен\n"
        + "/legal чтобы получить юридическую помощь\n"
        + "/evacuation общие чаты об эвакуации из Украины\n"
        + "/evacuation_cities чаты эвакуации по городам\n"
        + "/children_lessons онлайн уроки для детей из Украины\n"
        + "/handbook Методичка\n"
        + "/socialhelp Социальная помощь\n"
        + "/medial Медицинская помощь\n"
        + "/dentist Стоматологическая помощь\n"
        + "/jobs Работа в Германии\n"
        + "\n"
        + os.linesep
        + "Hi! Please use one of the following commands:\n"
        + "/cities to display existing chat for a city in Germany, you need to pass the name of the city: /cities name\n"
        + "/cities_all to display all existing chats for cities in Germany\n"
        + "/countries to display existing chats for the countries\n"
        + "/hryvnia to display information about hryvnia exchange\n"
        + "/legal to get information about legal help\n"
        + "/evacuation to get information about evacuation from Ukraine\n"
        + "/evacuation_cities evacuation chats for cities\n"
        + "/children_lessons online lessons for children from Ukraine\n"
        + "/handbook Handbook\n"
        + "/socialhelp Social help\n"
        + "/medial medical help\n"
        + "/dentist dentist help\n"
        + "/jobs Jobs in Germany\n"
        + "\n"
    )


def hryvnia():
    return get_from_knowledge(HRYVNIA_TITLE)


def jobs(book, name=None):
    return guidebook.get_info(book, "jobs", name)


def kids_with_special_needs():
    return get_from_knowledge(KIDS_WITH_SPECIAL_NEEDS_TITLE)

def legal():
    return get_from_knowledge(LEGAL_TITLE)


def medical(book, name=None):
    return guidebook.get_info(book, "medical", name)


def social_help():
    return get_from_knowledge(SOCIAL_HELP_TITLE)


def taxis(book):
    return guidebook.taxis(book)


def teachers_for_peace():
    return get_from_knowledge(TEACHERS_TITLE)


def translators():
     return get_from_knowledge(TRANSLATORS_TITLE)


def travel(book, name=None):
     return guidebook.get_info(book, "travel", name)


def volunteer(book, name=None):
    return guidebook.get_info(book, "volunteer", name)
