"""Unit tests for BerlinHelpService."""

from unittest.mock import Mock, patch
import pytest
from src.application.berlin_help_service import BerlinHelpService
from src.domain.protocols import IGuidebook


@pytest.fixture
def mock_guidebook():
    """Create a mock guidebook."""
    return Mock(spec=IGuidebook)


@pytest.fixture
def service(mock_guidebook):
    """Create a BerlinHelpService with mock guidebook."""
    return BerlinHelpService(guidebook=mock_guidebook)


class TestBerlinHelpService:
    """Test BerlinHelpService functionality."""

    @patch("src.application.berlin_help_service.wrap_with_separator")
    def test_handle_help(self, mock_wrap, service):
        """Test handle_help returns formatted help text."""
        mock_wrap.return_value = "=== FORMATTED HELP ==="

        result = service.handle_help()

        assert result == "=== FORMATTED HELP ==="
        mock_wrap.assert_called_once()
        # Verify the text contains expected multilingual content
        call_args = mock_wrap.call_args[0][0]
        assert "Привет" in call_args
        assert "Вітання" in call_args
        assert "Hi!" in call_args
        assert "Ukraine" in call_args or "Украины" in call_args

    @patch("src.application.berlin_help_service.format_contents")
    def test_handle_topic(self, mock_format, service, mock_guidebook):
        """Test handle_topic returns topic info with hashtag."""
        mock_guidebook.get_topic_contents.return_value = ["Item 1", "Item 2"]
        mock_format.return_value = "=== Formatted content ==="

        result = service.handle_topic("accommodation")

        assert result == "#accommodation\n=== Formatted content ==="
        mock_guidebook.get_topic_contents.assert_called_once_with("accommodation")
        mock_format.assert_called_once_with(["Item 1", "Item 2"])

    def test_handle_cities_with_name(self, service, mock_guidebook):
        """Test handle_cities with a city name."""
        mock_guidebook.get_cities.return_value = "Berlin info"

        result = service.handle_cities("Berlin", show_all=False)

        assert result == "Berlin info"
        mock_guidebook.get_cities.assert_called_once_with(name="Berlin")

    def test_handle_cities_without_name(self, service, mock_guidebook):
        """Test handle_cities without a city name."""
        mock_guidebook.get_cities.return_value = "Please specify city"

        result = service.handle_cities(None, show_all=False)

        assert result == "Please specify city"
        mock_guidebook.get_cities.assert_called_once_with(name=None)

    @patch("src.application.berlin_help_service.format_contents")
    def test_handle_cities_show_all(self, mock_format, service, mock_guidebook):
        """Test handle_cities with show_all flag."""
        mock_guidebook.get_topic_contents.return_value = {
            "Berlin": ["link1"],
            "Munich": ["link2"]
        }
        mock_format.return_value = "=== All cities ==="

        result = service.handle_cities(None, show_all=True)

        assert result == "=== All cities ==="
        mock_guidebook.get_topic_contents.assert_called_once_with("cities")
        mock_format.assert_called_once()

    def test_handle_countries_with_name(self, service, mock_guidebook):
        """Test handle_countries with a country name."""
        mock_guidebook.get_countries.return_value = "Poland info"

        result = service.handle_countries("Poland", show_all=False)

        assert result == "Poland info"
        mock_guidebook.get_countries.assert_called_once_with(name="Poland")

    def test_handle_countries_without_name(self, service, mock_guidebook):
        """Test handle_countries without a country name."""
        mock_guidebook.get_countries.return_value = "Please specify country"

        result = service.handle_countries(None, show_all=False)

        assert result == "Please specify country"
        mock_guidebook.get_countries.assert_called_once_with(name=None)

    @patch("src.application.berlin_help_service.format_contents")
    def test_handle_countries_show_all(self, mock_format, service, mock_guidebook):
        """Test handle_countries with show_all flag."""
        mock_guidebook.get_topic_contents.return_value = {
            "Poland": ["link1"],
            "Germany": ["link2"]
        }
        mock_format.return_value = "=== All countries ==="

        result = service.handle_countries(None, show_all=True)

        assert result == "=== All countries ==="
        mock_guidebook.get_topic_contents.assert_called_once_with("countries")
        mock_format.assert_called_once()

    def test_list_topics(self, service, mock_guidebook):
        """Test list_topics returns topic list from guidebook."""
        mock_guidebook.get_topics.return_value = ["accommodation", "transport", "cities"]

        result = service.list_topics()

        assert result == ["accommodation", "transport", "cities"]
        mock_guidebook.get_topics.assert_called_once()

    def test_get_topic_description(self, service, mock_guidebook):
        """Test get_topic_description returns description from guidebook."""
        mock_guidebook.get_topic_description.return_value = "Housing information"

        result = service.get_topic_description("accommodation")

        assert result == "Housing information"
        mock_guidebook.get_topic_description.assert_called_once_with("accommodation")

    def test_get_topic_description_nonexistent(self, service, mock_guidebook):
        """Test get_topic_description returns None for nonexistent topic."""
        mock_guidebook.get_topic_description.return_value = None

        result = service.get_topic_description("nonexistent")

        assert result is None
        mock_guidebook.get_topic_description.assert_called_once_with("nonexistent")
