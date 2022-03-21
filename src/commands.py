import os
import knowledge

HANDBOOK_TITLE = "Mетодичка"
HRYVNIA_TITLE = "Обмен гривен/Exchange hryvnia"
KIDS_WITH_SPECIAL_NEEDS_TITLE = (
    "Дети с особыми образовательными потребностями/Kids with special needs"
)
LEGAL_TITLE = "Юридическая помощь/Legal help"
SOCIAL_HELP_TITLE = "Социальная помощь"
TEACHERS_TITLE = "Онлайн уроки для детей/Online lessons for children"
TRANSLATORS_TITLE = "Переводчики/Translators"
BEAUTY_TITLE = "Beauty"
PSYCHOLOGICAL_HELP_TITLE = "Психологическая помощь/Psychological help"
ACCOMODATION_TITLE = "Проживание/Stay"
SOCIAL_ADAPTION_TITLE = "Группа социальной адаптации/Social adaption"
GENERAL_INFO_TITLE = "Информация"
OFFICIAL_INFO_TITLE = "Официальная информация/Official statements"



def get_from_knowledge(title):
    replies = knowledge.replies
    return [p for p in replies if p.title == title][0].content


def handbook():
    return get_from_knowledge(HANDBOOK_TITLE)


def hryvnia():
    return get_from_knowledge(HRYVNIA_TITLE)


def kids_with_special_needs():
    return get_from_knowledge(KIDS_WITH_SPECIAL_NEEDS_TITLE)


def legal():
    return get_from_knowledge(LEGAL_TITLE)


def social_help():
    return get_from_knowledge(SOCIAL_HELP_TITLE)


def teachers_for_peace():
    return get_from_knowledge(TEACHERS_TITLE)


def translators():
    return get_from_knowledge(TRANSLATORS_TITLE)


def beauty():
    return get_from_knowledge(BEAUTY_TITLE)


def psychological_help():
    return get_from_knowledge(PSYCHOLOGICAL_HELP_TITLE)


def accomodation():
    return get_from_knowledge(ACCOMODATION_TITLE)


def social_adaption():
    return get_from_knowledge(SOCIAL_ADAPTION_TITLE)


def general_information():
    return get_from_knowledge(GENERAL_INFO_TITLE)


def official_information():
    return get_from_knowledge(OFFICIAL_INFO_TITLE)


def help():
    return (
        "Привет! Используйте одну из команд:\n"
        + "/beauty beauty сообщества \n"
        + "/cities чтобы увидеть чат помощи по городам Германии, вам нужно "
        + "написать название города: /cities name\n"
        + "/cities_all чтобы увидеть все чаты помощи по городам Германии\n"
        + "/countries чтобы увидеть все чаты помощи по странам\n"
        + "/hryvnia чтобы получить информацию про обмен гривен\n"
        + "/legal чтобы получить юридическую помощь\n"
        + "/evacuation общие чаты об эвакуации из Украины\n"
        + "/evacuation_cities чаты эвакуации по городам\n"
        + "/children_lessons онлайн уроки для детей из Украины\n"
        + "/handbook Методичка\n"
        + "/socialhelp Социальная помощь\n"
        + "/medical Медицинская помощь\n"
        + "/dentist Стоматологическая помощь\n"
        + "/jobs Работа в Германии\n"
        + "/disabled информация для людей с ограниченными возможностями \n"
        + "/psylogical псиохологическая помощь \n"
        + "\n"
        + os.linesep
        + "Hi! Please use one of the following commands:\n"
        + "/beauty beauty groups\n"
        + "/cities to display existing chat for a city in Germany, you need "
        + "to pass the name of the city: /cities name\n"
        + "/cities_all to display all existing chats for cities in Germany\n"
        + "/countries to display existing chats for the countries\n"
        + "/hryvnia to display information about hryvnia exchange\n"
        + "/legal to get information about legal help\n"
        + "/evacuation to get information about evacuation from Ukraine\n"
        + "/evacuation_cities evacuation chats for cities\n"
        + "/children_lessons online lessons for children from Ukraine\n"
        + "/handbook Handbook\n"
        + "/socialhelp Social help\n"
        + "/medical medical help\n"
        + "/dentist dentist help\n"
        + "/jobs Jobs in Germany\n"
        + "/disabled information for people with disabilities\n"

        + "/psylogical psylogical рудз\n"
        + "\n"
    )
