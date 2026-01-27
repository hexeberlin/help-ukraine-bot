"""Telegram authorization adapter - Handles Telegram-specific auth checks."""

from telegram import Bot


class TelegramAuthorizationAdapter:
    """Adapter for Telegram-specific authorization operations."""

    async def is_user_admin(self, user_id: int, chat_id: int, bot: Bot) -> bool:
        """
        Check if a user is an admin in a specific chat.

        Args:
            user_id: The user ID to check
            chat_id: The chat ID to check in
            bot: The Telegram bot instance

        Returns:
            True if user is admin, False otherwise
        """
        admins = [
            member.user.id
            for member in await bot.get_chat_administrators(chat_id=chat_id)
        ]
        return user_id in admins
