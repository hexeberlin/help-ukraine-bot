"""main module running the bot"""

from src.infrastructure.config_loader import load_env_config, load_toml_settings
from src.infrastructure.yaml_guidebook import YamlGuidebook
from src.infrastructure.sqlite_statistics import StatisticsServiceSQLite
from src.application.berlin_help_service import BerlinHelpService
from src.adapters.telegram_adapter import TelegramBotAdapter


def main() -> None:
    """Start the bot with dependency injection."""
    # 1. Load configuration
    app_name, token, port = load_env_config()
    settings = load_toml_settings("settings.toml")

    # 2. Create infrastructure (concrete implementations)
    guidebook = YamlGuidebook(
        guidebook_path=settings["GUIDEBOOK_PATH"],
        vocabulary_path=settings["VOCABULARY_PATH"]
    )

    # 3. Create application services
    berlin_help_service = BerlinHelpService(guidebook=guidebook)
    stats_service = StatisticsServiceSQLite()

    # 4. Create adapter
    telegram_adapter = TelegramBotAdapter(
        token=token,
        service=berlin_help_service,
        guidebook=guidebook,
        stats_service=stats_service,
    )

    # 5. Build and run
    application = telegram_adapter.build_application()

    if app_name == "TESTING":
        application.run_polling()
    else:
        webhook_url = f"https://{app_name}.herokuapp.com/{token}"
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=webhook_url,
        )


if __name__ == "__main__":
    main()
