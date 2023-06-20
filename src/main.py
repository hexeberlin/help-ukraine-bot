"""main module running the bot"""

from telegram.ext import Filters, InlineQueryHandler, MessageHandler, Updater

from src import commands
from src.config import APP_NAME, PORT, TOKEN


def main() -> None:
    """Start the bot"""
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    command_list = sorted(commands.add_commands(dispatcher), key=lambda c: c.command)

    updater.bot.set_my_commands(command_list)

    # Messages
    dispatcher.add_handler(MessageHandler(Filters.all, commands.delete_greetings))

    # Inlines
    dispatcher.add_handler(InlineQueryHandler(commands.find_articles_command))

    if APP_NAME == "TESTING":
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
        updater.bot.setWebhook(f"https://{APP_NAME}.herokuapp.com/{TOKEN}")

    updater.idle()


if __name__ == "__main__":
    main()
