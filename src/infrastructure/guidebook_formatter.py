"""Guidebook content formatting utilities.

This module handles the formatting of guidebook contents into human-readable strings.
Formatting is an infrastructure concern (presentation/technical detail), not business logic.
"""

from typing import Dict, List, Optional
from src.domain.protocols import GuidebookContent


def wrap_with_separator(text: str) -> str:
    """Wrap text with separator lines.

    Args:
        text: Text to wrap

    Returns:
        Text with "======..." separator lines above and below
    """
    separator = "=" * 30
    return f"{separator}\n{text}{separator}"


def format_contents(
    contents: GuidebookContent,
    title: Optional[str] = None
) -> str:
    """Format guidebook contents into a readable string.

    Args:
        contents: Either a list of strings or a dict mapping keys to lists
        title: Optional title to display at the top (will be title-cased)

    Returns:
        Formatted string with separator lines

    Examples:
        List contents:
            format_contents(["Item 1", "Item 2"])
            => "======...\\nItem 1\\nItem 2\\n======..."

        Dict contents (section headers or subtopics):
            format_contents({"Berlin": ["link1"], "Munich": ["link2"]})
            => "======...\\nBerlin:\\n- link1\\nMunich:\\n- link2\\n======..."

        With title:
            format_contents(["Item 1"], title="Berlin")
            => "======...\\nBerlin\\nItem 1\\n======..."
    """
    if isinstance(contents, list):
        return _format_list_contents(contents, title)
    if isinstance(contents, dict):
        return _format_dict_contents(contents)
    raise TypeError(
        f"contents must be list or dict, got {type(contents).__name__}. "
        f"This should have been caught by guidebook validation - "
        f"please report this as a bug."
    )


def _format_list_contents(items: List[str], title: Optional[str] = None) -> str:
    """Format list-based contents.

    Args:
        items: List of strings to format
        title: Optional title to display at the top

    Returns:
        Formatted string with separator lines
    """
    result = ""
    if title:
        result = f"{title.title()}\n"

    for item in items:
        result += item + "\n"

    return wrap_with_separator(result)


def _format_dict_contents(sections: Dict[str, List[str]]) -> str:
    """Format dict-based contents.

    Each key becomes a section header with its list items as bullet points.
    This applies to both topics with section headers (e.g., 'animals') and
    topics with subtopics (e.g., 'cities', 'countries').

    Args:
        sections: Dict mapping section names/subtopics to lists of items

    Returns:
        Formatted string with separator lines
    """
    result = ""
    for key, values in sections.items():
        result += f"{key}:\n"
        for value in values:
            result += f"- {value}\n"

    return wrap_with_separator(result)
