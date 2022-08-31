from telegram import (
    Update,
    Message,
)
from telegram.ext import CommandHandler

statistics_database = {}


class StatisticsCommandHandler(CommandHandler):
    def handle_update(self, update: Update, dispatcher, check_result, context=None):
        msg: Message = update.message
        user_id = msg.from_user.id
        chat_id = msg.chat_id
        id = f"{chat_id}:{user_id}"

        if id not in statistics_database:
            statistics_database[id] = {}

        if msg.text not in statistics_database[id]:
            statistics_database[id][msg.text] = 0

        statistics_database[id][msg.text] += 1

        CommandHandler.handle_update(self, update, dispatcher, check_result, context)
