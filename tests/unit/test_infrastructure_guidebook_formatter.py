"""Unit tests for infrastructure guidebook_formatter module."""

import pytest
from src.infrastructure.guidebook_formatter import (
    format_contents,
    wrap_with_separator,
)


class TestWrapWithSeparator:
    """Test wrap_with_separator function."""

    def test_wraps_text_with_separator_lines(self):
        """Test that text is wrapped with separator lines."""
        text = "Test content"
        result = wrap_with_separator(text)

        # Should contain separator lines
        assert "=" * 30 in result
        # Should contain the original text
        assert "Test content" in result
        # Should have separator at start and end
        lines = result.split("\n")
        assert "=" in lines[0]
        assert "=" in lines[-1]

    def test_preserves_multiline_text(self):
        """Test that multiline text is preserved."""
        text = "Line 1\nLine 2\nLine 3"
        result = wrap_with_separator(text)

        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result


class TestFormatContents:
    """Test format_contents function."""

    def test_format_list_contents_without_title(self):
        """Test formatting list-based contents without title."""
        contents = ["Item 1", "Item 2", "Item 3"]
        result = format_contents(contents)

        # Should contain all items
        assert "Item 1" in result
        assert "Item 2" in result
        assert "Item 3" in result
        # Should have separator lines
        assert "=" * 30 in result

    def test_format_list_contents_with_title(self):
        """Test formatting list-based contents with title."""
        contents = ["Link 1", "Link 2"]
        result = format_contents(contents, title="Berlin")

        # Should contain title (title-cased)
        assert "Berlin" in result
        # Should contain items
        assert "Link 1" in result
        assert "Link 2" in result
        # Should have separator lines
        assert "=" * 30 in result

    def test_format_dict_contents_without_title(self):
        """Test formatting dict-based contents without title."""
        contents = {
            "Berlin": ["https://t.me/berlinhelp"],
            "Munich": ["https://t.me/munichhelp", "https://t.me/munichsupport"],
        }
        result = format_contents(contents)

        # Should contain section headers
        assert "Berlin:" in result
        assert "Munich:" in result
        # Should contain items with bullet points
        assert "- https://t.me/berlinhelp" in result
        assert "- https://t.me/munichhelp" in result
        assert "- https://t.me/munichsupport" in result
        # Should have separator lines
        assert "=" * 30 in result

    def test_format_dict_contents_with_title(self):
        """Test formatting dict-based contents with title (title currently unused)."""
        contents = {
            "Section 1": ["Item A"],
            "Section 2": ["Item B"],
        }
        result = format_contents(contents, title="Topic")

        # Should contain section headers
        assert "Section 1:" in result
        assert "Section 2:" in result
        # Should contain items
        assert "- Item A" in result
        assert "- Item B" in result

    def test_format_dict_with_cyrillic_keys(self):
        """Test formatting dict with Cyrillic section headers."""
        contents = {
            "Полезные ссылки": ["https://tasso.net"],
            "Бесплатная помощь": ["https://example.com"],
        }
        result = format_contents(contents)

        # Should contain Cyrillic headers
        assert "Полезные ссылки:" in result
        assert "Бесплатная помощь:" in result
        # Should contain links
        assert "- https://tasso.net" in result
        assert "- https://example.com" in result

    def test_format_empty_list(self):
        """Test formatting empty list."""
        contents = []
        result = format_contents(contents)

        # Should still have separator lines
        assert "=" * 30 in result

    def test_format_empty_dict(self):
        """Test formatting empty dict."""
        contents = {}
        result = format_contents(contents)

        # Should still have separator lines
        assert "=" * 30 in result

    def test_raises_type_error_for_invalid_type(self):
        """Test that TypeError is raised for invalid content types."""
        with pytest.raises(TypeError):
            format_contents("invalid_string")  # type: ignore

        with pytest.raises(TypeError):
            format_contents(123)  # type: ignore
