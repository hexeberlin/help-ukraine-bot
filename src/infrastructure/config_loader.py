"""Configuration loading utilities."""

import configparser
from os import environ as env
from typing import Tuple, Dict, Any
import toml


def load_env_config() -> Tuple[str, str, int]:
    """
    Load environment configuration.

    Returns:
        Tuple of (app_name, token, port)
    """
    parser = configparser.ConfigParser()
    parser.read("settings.env")

    try:
        app_name = env["APP_NAME"]
        token = env["TOKEN"]
    except KeyError:
        app_name = parser.get("DEVELOPMENT", "APP_NAME")
        token = parser.get("DEVELOPMENT", "TOKEN")

    port = int(env.get("PORT", 5000))

    return app_name, token, port


def load_toml_settings(filepath: str) -> Dict[str, Any]:
    """
    Load TOML configuration file.

    Args:
        filepath: Path to TOML settings file

    Returns:
        Dictionary of settings
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return toml.load(f)
