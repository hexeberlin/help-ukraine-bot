"""main module running the bot"""

from src.infrastructure.config_loader import load_env_config, load_toml_settings
from src.infrastructure.yaml_guidebook import YamlGuidebook
from src.infrastructure.sqlite_statistics import StatisticsServiceSQLite
from src.application.berlin_help_service import BerlinHelpService
from src.application.authorization_service import AuthorizationService
from src.adapters.telegram_auth import TelegramAuthorizationAdapter
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
    auth_service = AuthorizationService(
        admin_only_chat_ids={-1001723117571, -735136184}
    )
    stats_service = StatisticsServiceSQLite()

    # 4. Create adapters
    telegram_auth = TelegramAuthorizationAdapter()
    telegram_adapter = TelegramBotAdapter(
        token=token,
        service=berlin_help_service,
        guidebook_topics=guidebook.get_topics(),
        guidebook_descriptions=guidebook.get_descriptions(),
        auth_service=auth_service,
        stats_service=stats_service,
        telegram_auth=telegram_auth,
        berlin_chat_ids=[-1001589772550, -1001790676165, -735136184],
        reminder_interval_pinned=30 * 60,
        reminder_interval_info=10 * 60,
        reminder_message="I WILL POST PINNED MESSAGE HERE",
        pinned_job_name="pinned",
        social_job_name="social",
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
