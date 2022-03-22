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
GENERAL_INFO_TITLE = "Информация"
OFFICIAL_INFO_TITLE = "Официальная информация/Official statements"
BANKING_TITLE = "Banking"
EDUCATION_TITLE = "Education"
MINORS_TITLE = "Minors"


def get_from_knowledge(title):
    replies = knowledge.replies
    return [p for p in replies if p.title == title][0].content


def banking():
    return get_from_knowledge(BANKING_TITLE)

def education():
    return get_from_knowledge(EDUCATION_TITLE)

def handbook():
    return get_from_knowledge(HANDBOOK_TITLE)


def hryvnia():
    return get_from_knowledge(HRYVNIA_TITLE)


def kids_with_special_needs():
    return get_from_knowledge(KIDS_WITH_SPECIAL_NEEDS_TITLE)


def legal():
    return get_from_knowledge(LEGAL_TITLE)


def minors():
    return get_from_knowledge(MINORS_TITLE)

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

def general_information():
    return get_from_knowledge(GENERAL_INFO_TITLE)


def official_information():
    return get_from_knowledge(OFFICIAL_INFO_TITLE)


def help():
    return (
        "Привет! 🤖 "
        + os.linesep
        + "Я бот для помощи беженцам из Украины 🇺🇦 в Германии. "
        + os.linesep
        + "Большинство моих знаний относятся к Берлину, но есть и общая "
        + "полезная информация. Чтобы увидеть список поддерживаемых команд, "
        + "введите символ '/'. "
        + "\n\n"
        + "Если добавите меня в свой чат, не забудьте дать мне права "
        + "админа, пожалуйста, чтобы я мог удалять ненужные сообщения с "
        + "вызванными командами."
        + "\n\n\n"
        + "Вітання! 🤖 "
        + os.linesep
        + "Я бот для допомоги біженцям з України 🇺🇦 в Німеччині."
        + os.linesep
        + "Більшість моїх знань стосуються Берліну, але є й загальна "
        + "корисна інформація. Щоб побачити список команд, що підтримуються, "
        + "введіть символ '/'. "
        + "\n\n"
        + "Якщо додасте мене до свого чату, будь ласка, не забудьте надати "
        + "мені права адміна, щоб я зміг видаляти непотрібні повідомлення із "
        + "викликаними командами."
        + "\n\n\n"
        + "Hi! 🤖"
        + os.linesep
        + "I'm the bot helping refugees from Ukraine 🇺🇦 in Germany. "
        + os.linesep
        + "Most of my knowledge concentrates around Berlin, but I have some "
        + "general useful information too. Type '/' to see the list of my "
        + "available commands."
        + "\n\n"
        + "If you add me to your chat, don't forget to give me the admin "
        + "rights, so that I can delete log messages and keep your chat clean."
    )
