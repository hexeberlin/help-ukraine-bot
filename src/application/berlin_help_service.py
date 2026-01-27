"""Berlin help service - Core business logic for handling user requests."""

import os
from typing import Optional
from src.domain.protocols import IGuidebook


class BerlinHelpService:
    """Service handling business logic for Berlin help requests."""

    def __init__(self, guidebook: IGuidebook) -> None:
        """
        Initialize the service.

        Args:
            guidebook: Guidebook data access implementation
        """
        self.guidebook = guidebook

    def handle_help(self) -> str:
        """
        Handle help command - return help text with available topics.

        Returns:
            Formatted help text in multiple languages
        """
        help_text = (
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
            + "I'm a bot helping refugees from Ukraine 🇺🇦 in Germany. "
            + os.linesep
            + "Most of my knowledge focuses on Berlin, but I have some "
            + "general useful information too. Type '/' to see the list of my "
            + "available commands."
            + "\n\n"
            + "If you add me to your chat, don't forget to grant me admin "
            + "rights, so that I can delete log messages and keep your chat clean."
        )
        return self.guidebook.format_results(help_text)

    def handle_topic(self, topic_name: str) -> str:
        """
        Handle topic request - return formatted topic information.

        Args:
            topic_name: Name of the topic to retrieve

        Returns:
            Formatted topic information with hashtag
        """
        info = self.guidebook.get_results(topic_name)
        return f"#{topic_name}\n{info}"

    def handle_cities(self, city_name: Optional[str], show_all: bool = False) -> str:
        """
        Handle cities command - return city information.

        Args:
            city_name: Name of the city (None to show prompt or all)
            show_all: Whether to show all cities

        Returns:
            Formatted city information
        """
        if show_all:
            return self.guidebook.get_info("cities", name=None)
        return self.guidebook.get_cities(name=city_name)

    def handle_countries(self, country_name: Optional[str], show_all: bool = False) -> str:
        """
        Handle countries command - return country information.

        Args:
            country_name: Name of the country (None to show prompt or all)
            show_all: Whether to show all countries

        Returns:
            Formatted country information
        """
        if show_all:
            return self.guidebook.get_info("countries", name=None)
        return self.guidebook.get_countries(name=country_name)

    def handle_social_reminder(self) -> str:
        """
        Handle social reminder - return social help information.

        Returns:
            Social help content from guidebook
        """
        return self.guidebook.get_results("social_help")
