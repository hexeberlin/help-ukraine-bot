"""main module running the bot"""

from telegram.ext import Application, MessageHandler, filters

from src import commands
from src.config import APP_NAME, PORT, TOKEN


def main() -> None:
    """Start the bot"""
    application = Application.builder().token(TOKEN).build()

    command_list = sorted(commands.register(application), key=lambda c: c.command)

    async def _post_init(app: Application) -> None:
        await app.bot.set_my_commands(command_list)

    application.post_init = _post_init

    # Messages
    application.add_handler(MessageHandler(filters.ALL, commands.delete_greetings))

    if APP_NAME == "TESTING":
        application.run_polling()
    else:
        webhook_url = f"https://{APP_NAME}.herokuapp.com/{TOKEN}"
        application.run_webhook(
            listen="0.0.0.0",
            port=int(PORT),
            url_path=TOKEN,
            webhook_url=webhook_url,
        )


if __name__ == "__main__":
    main()
