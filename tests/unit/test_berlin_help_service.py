"""Unit tests for BerlinHelpService."""

from unittest.mock import Mock
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

    def test_handle_help(self, service, mock_guidebook):
        """Test handle_help returns formatted help text."""
        mock_guidebook.format_results.return_value = "=== FORMATTED HELP ==="

        result = service.handle_help()

        assert result == "=== FORMATTED HELP ==="
        mock_guidebook.format_results.assert_called_once()
        # Verify the text contains expected multilingual content
        call_args = mock_guidebook.format_results.call_args[0][0]
        assert "Привет" in call_args
        assert "Вітання" in call_args
        assert "Hi!" in call_args
        assert "Ukraine" in call_args or "Украины" in call_args

    def test_handle_topic(self, service, mock_guidebook):
        """Test handle_topic returns topic info with hashtag."""
        mock_guidebook.get_results.return_value = "Topic information"

        result = service.handle_topic("accommodation")

        assert result == "#accommodation\nTopic information"
        mock_guidebook.get_results.assert_called_once_with("accommodation")

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

    def test_handle_cities_show_all(self, service, mock_guidebook):
        """Test handle_cities with show_all flag."""
        mock_guidebook.get_info.return_value = "All cities info"

        result = service.handle_cities(None, show_all=True)

        assert result == "All cities info"
        mock_guidebook.get_info.assert_called_once_with("cities", name=None)

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

    def test_handle_countries_show_all(self, service, mock_guidebook):
        """Test handle_countries with show_all flag."""
        mock_guidebook.get_info.return_value = "All countries info"

        result = service.handle_countries(None, show_all=True)

        assert result == "All countries info"
        mock_guidebook.get_info.assert_called_once_with("countries", name=None)
