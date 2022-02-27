from telegram import Update
import requests
import telegram
import os
TOKEN = os.environ["TOKEN"]

def webhook(request):
    bot = telegram.Bot(token=TOKEN)
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id
        reminder_message = """
                    Dear group members,
                    We remind you that this is a group for helping and finding help. Please refrain from putting unrelated entries here. Anybody adding hate or trolling comments will be banned from the group.
                    The overview of useful links  about documents, transport, accommodation etc. can be found here https://bit.ly/help-for-ukrainians

                    Уважаемые участники группы,
                    Напоминаем вам, что цель этой группы – предоставление и поиск помощи. Пожалуйста, воздержитесь от размещения здесь записей, не имеющих отношения к теме. Пользователи, добавляющие агрессивные или тролящие комментарии,  будут удаляны из группы.
                    Обзор полезных ссылок о документах, транспорте, жилье и т.д. можно найти здесь
                     https://bit.ly/help-for-ukrainians

                    Шановні учасники групи
                    Нагадуємо вам, що це група для допомоги та пошуку допомоги. Будь ласка, утримайтеся від розміщення записів, що не мають відношення до теми. Будь-хто, хто додаватиме коментарі ненависті або тролінгу, буде видалено з групи.
                    Огляд корисних посилань про документи, транспорт, житло тощо. можна знайти тут
                     https://bit.ly/help-for-ukrainians
        """
        bot.sendMessage(chat_id=chat_id, text=reminder_message)
    return "OK"