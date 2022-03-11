import os

import guidebook
import knowledge


HRYVNIA_TITLE = "Обмен гривен/Exchange hryvnia"
LEGAL_TITLE = "Юридическая помощь/Legal help"
TEACHERS_TITLE = "Онлайн уроки для детей/Online lessons for children"


def get_from_knowledge(title):
    replies = knowledge.replies
    return [p for p in replies if p.title == title][0].content


def cities(book, name=None):
    return guidebook.cities_chats(book, name)


def countries(book, name=None):
    return guidebook.countries_chats(book, name)


def help():
    return ("Привет! Используйте одну из команд: "
           + "/cities чтобы увидеть все чаты помощи по городам Германии"
           + "/countries чтобы увидеть все чаты помощи по странам"
           + "/hryvnia чтобы получить информацию про обмен гривен"
           + "/legal чтобы получить юридическую помощь"
           + "/evacuation общие чаты об эвакуации из Украины"
           + "/evacuationCities чаты эвакуации по городам"
           + "/childrenLessons онлайн уроки для детей из Украины"
           + os.linesep()
           + "Hi! Please use one of the following commands: "
           + "/cities to display existing chats for cities in Germany"
           + "/countries to display existing chats for the countries"
           + "/hryvnia to display information about hryvnia exchange"
           + "/legal to get information about legal help"
           + "/evacuation to get information about evacuation from Ukraine"
           + "/evacuationCities evacuation chats for cities"
           + "/childrenLessons online lessons for children from Ukraine")


def hryvnia():
    return get_from_knowledge(HRYVNIA_TITLE)


def legal():
    return get_from_knowledge(LEGAL_TITLE)


def teachers_for_peace():
    return get_from_knowledge(TEACHERS_TITLE)


def evacuation(book):
    return guidebook.evacuation(book)


def evacuation_cities(book, name=None):
    return guidebook.evacuation_cities(book, name)
