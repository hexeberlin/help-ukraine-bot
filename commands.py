import guidebook
import knowledge


def cities(book, name=None):
    return guidebook.cities(book, name)


def countries(book, name=None):
    return guidebook.countries(book, name)


def hryvnia():
    replies = knowledge.replies
    return any(x for x in replies if x.title == "Обмен гривен/Exchange hryvnia")