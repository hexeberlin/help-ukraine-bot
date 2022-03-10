import guidebook
import knowledge

HRYVNIA_TITLE = "Обмен гривен/Exchange hryvnia"
LEGAL_TITLE = "Юридическая помощь/Legal help"


def get_from_knowledge(title):
    replies = knowledge.replies
    return [p for p in replies if p.title == title][0].content


def cities(book, name=None):
    return guidebook.cities(book, name)


def countries(book, name=None):
    return guidebook.countries(book, name)


def hryvnia():
    return get_from_knowledge(HRYVNIA_TITLE)


def legal():
    return get_from_knowledge(LEGAL_TITLE)
