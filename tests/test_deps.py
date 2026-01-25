from __future__ import annotations

import importlib

import telegram


def _version_tuple(version: str) -> tuple[int, ...]:
    """Convert version strings like '21.11.1' into a tuple for comparisons."""
    return tuple(int(part) for part in version.split(".") if part.isdigit())


def test_python_telegram_bot_version():
    """Ensure we are running on the expected PTB major/minor release."""
    assert _version_tuple(telegram.__version__) >= (21, 11)


def test_webhook_extra_installed():
    """The webhook extra requires tornado; ensure it's importable."""
    tornado = importlib.import_module("tornado")
    assert tornado is not None
