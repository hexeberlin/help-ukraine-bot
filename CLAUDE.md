# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot providing FAQ answers and helpful information for Ukrainian refugees in Germany, primarily focused on Berlin. Built with python-telegram-bot and MongoDB.

## Build & Development Commands

```bash
# Setup environment (Python 3.11 per runtime.txt)
python3.11 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run locally (requires settings.env with credentials)
python -m src.main

# Run tests
pytest tests
pytest tests/test_guidebook.py  # single test file

# Lint (CI runs with -E flag for errors only)
pylint -E src tests
```

## Configuration

Local development requires `settings.env`:
```env
[DEVELOPMENT]
APP_NAME=TESTING
TOKEN=<telegram_bot_token>
MONGO_HOST=<host>
MONGO_USER=<user>
MONGO_PASS=<password>
MONGO_BASE=<database>
```

`settings.toml` defines paths to knowledge base files and is read at runtime.

## Architecture

**Entry point**: `src/main.py` - Initializes the Telegram Updater, registers command handlers from `src/commands.py`, and starts either polling (local dev) or webhook mode (Heroku production).

**Knowledge base system**:
- `src/knowledgebase/guidebook.yml` - Primary content: topics mapped to information lists/dicts
- `src/knowledgebase/vocabulary.yml` - Aliases for city/topic name lookups
- `src/guidebook.py` - `Guidebook` class loads YAML and provides `get_info()`, `get_cities()`, `get_countries()` methods. `NameType` enum defines all valid topic keys.

**Commands**: `src/commands.py` dynamically generates handlers for each topic in the guidebook. Special handling for `/cities` and `/countries` which take parameters. Admin-restricted commands use `@restricted` decorator from `src/common.py`.

**Articles service**: `src/services/articles.py` - MongoDB-backed FAQ storage for user-contributed content, accessed via inline queries.

**MongoDB**: `src/mongo/__init__.py` - Connection helper returning a database handle.

## Key Patterns

- Bot commands are auto-registered from guidebook keys; add new topics by adding entries to `guidebook.yml` with matching `NameType` enum values
- City/country name aliases go in `vocabulary.yml` (lowercase keys)
- The `@restricted` decorator limits commands to chat admins
- APP_NAME="TESTING" triggers polling mode; any other value uses webhooks

## Deployment

Main branch auto-deploys to Heroku on PR merge. The bot needs admin rights in chats to delete command messages.
