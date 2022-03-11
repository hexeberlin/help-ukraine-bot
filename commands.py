import os

import guidebook
import knowledge


HRYVNIA_TITLE = "Обмен гривен/Exchange hryvnia"
LEGAL_TITLE = "Юридическая помощь/Legal help"
TEACHERS_TITLE = "Онлайн уроки для детей/Online lessons for children"
HANDBOOK_TITLE = "Mетодичка"


def get_from_knowledge(title):
    replies = knowledge.replies
    return [p for p in replies if p.title == title][0].content


def cities(book, name=None):
    return guidebook.cities_chats(book, name)


def countries(book, name=None):
    return guidebook.countries_chats(book, name)


def help():
    return ("Привет! Используйте одну из команд:\n"
           + "/cities чтобы увидеть все чаты помощи по городам Германии\n"
           + "/countries чтобы увидеть все чаты помощи по странам\n"
           + "/hryvnia чтобы получить информацию про обмен гривен\n"
           + "/legal чтобы получить юридическую помощь\n"
           + "/evacuation общие чаты об эвакуации из Украины\n"
           + "/evacuationCities чаты эвакуации по городам\n"
           + "/childrenLessons онлайн уроки для детей из Украины\n\n"
           + os.linesep
           + "Hi! Please use one of the following commands:\n"
           + "/cities to display existing chats for cities in Germany\n"
           + "/countries to display existing chats for the countries\n"
           + "/hryvnia to display information about hryvnia exchange\n"
           + "/legal to get information about legal help\n"
           + "/evacuation to get information about evacuation from Ukraine\n"
           + "/evacuationCities evacuation chats for cities\n"
           + "/childrenLessons online lessons for children from Ukraine")


def hryvnia():
    return get_from_knowledge(HRYVNIA_TITLE)


def legal():
    return get_from_knowledge(LEGAL_TITLE)


def teachers_for_peace():
    return get_from_knowledge(TEACHERS_TITLE)


def handbook():
    return get_from_knowledge(HANDBOOK_TITLE)


def evacuation(book):
    return guidebook.evacuation(book)


def evacuation_cities(book, name=None):
    return guidebook.evacuation_cities(book, name)
