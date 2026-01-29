# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot providing FAQ answers and helpful information for Ukrainian refugees in Germany, primarily focused on Berlin. Built with python-telegram-bot and Clean Architecture principles.

## Build & Development Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Setup environment (Python 3.11)
# uv automatically creates and manages virtual environments
uv sync

# Run locally (requires settings.env with credentials)
uv run python -m src.main

# Run tests
uv run pytest tests
uv run pytest tests/unit/  # unit tests only
uv run pytest tests/integration/  # integration tests only

# Lint (CI runs with -E flag for errors only)
uv run pylint -E src tests

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Update dependencies
uv lock --upgrade
```

**Important Notes:**
- Heroku natively supports uv and uses `uv.lock` for deployments
- Always commit both `pyproject.toml` and `uv.lock` when dependencies change
- No need for `requirements.txt` - Heroku reads directly from `uv.lock`

## Configuration

Local development requires `settings.env`:
```env
[DEVELOPMENT]
APP_NAME=TESTING
TOKEN=<telegram_bot_token>
```

`settings.toml` defines paths to knowledge base files and is read at runtime.

## Architecture

The project follows Clean Architecture with clear layer separation:

```
Domain (Protocols) → Application (Services) → Adapter (Telegram) → Infrastructure (YAML)
```

### Entry Point

`src/main.py` - Constructs the application using dependency injection:
1. Loads configuration from environment and TOML files
2. Creates infrastructure layer (YamlGuidebook, StatisticsServiceSQLite)
3. Creates application service (BerlinHelpService)
4. Creates adapter (TelegramBotAdapter)
5. Builds and runs the Telegram Application

### Layer Details

**Domain Layer** (`src/domain/`):
- `protocols.py` - Interfaces (IGuidebook, IBerlinHelpService, IStatisticsService)
- `models.py` - Value objects (ChatContext, CommandRequest)

**Application Layer** (`src/application/`):
- `berlin_help_service.py` - Core business logic for handling help requests

**Adapter Layer** (`src/adapters/`):
- `telegram_adapter.py` - Telegram-specific bot logic, handler registration, and message handling

**Infrastructure Layer** (`src/infrastructure/`):
- `yaml_guidebook.py` - YAML-based guidebook implementation
- `config_loader.py` - Configuration loading utilities
- `sqlite_statistics.py` - In-memory SQLite statistics storage

**Knowledge Base**:
- `src/knowledgebase/guidebook.yml` - Primary content: topics mapped to information lists/dicts
- `src/knowledgebase/vocabulary.yml` - Aliases for city/topic name lookups

### Request Flow

1. Telegram Update → TelegramBotAdapter handler
2. Handler calls BerlinHelpService method
3. Service calls YamlGuidebook for data
4. Service returns formatted result
5. Adapter records topic statistics via StatisticsServiceSQLite
6. Adapter sends reply via Telegram API

## Key Patterns

### Adding New Features

**New topic in guidebook:**
1. Add entry to `src/knowledgebase/guidebook.yml`
2. Bot automatically registers handler on next deployment
3. No code changes needed

**New command requiring custom logic:**
1. Add method to `IBerlinHelpService` protocol
2. Implement in `BerlinHelpService`
3. Add handler method in `TelegramBotAdapter`
4. Register handler in `_register_handlers()`

**New stats aggregation:**
1. Extend `IStatisticsService` in `src/domain/protocols.py`
2. Implement in `StatisticsServiceSQLite`
3. Call from adapter handlers only

**New data source:**
1. Define protocol in `src/domain/protocols.py`
2. Implement in `src/infrastructure/`
3. Inject via `main.py`

### Testing Strategy

- **Unit tests** (`tests/unit/`) - Test services and adapters with mocks
- **Integration tests** (`tests/integration/`) - Test services with real guidebook data
- Use `Mock(spec=IProtocol)` for dependency mocking
- Use `@pytest.mark.anyio` for async tests

### Dependency Injection

All dependencies are injected via constructors in `main.py`. No global state or mutable singletons.

## Deployment

Main branch auto-deploys to Heroku on PR merge. The bot needs admin rights in chats to delete command messages.

- APP_NAME="TESTING" triggers polling mode (local dev)
- Any other APP_NAME uses webhooks (Heroku production)

## File Structure

```
src/
├── domain/
│   ├── protocols.py      # Interfaces
│   └── models.py         # Value objects
├── application/
│   └── berlin_help_service.py
├── adapters/
│   └── telegram_adapter.py
├── infrastructure/
│   ├── yaml_guidebook.py
│   ├── sqlite_statistics.py
│   └── config_loader.py
├── knowledgebase/
│   ├── guidebook.yml
│   └── vocabulary.yml
├── config.py            # Legacy config (kept for compatibility)
└── main.py              # Entry point with DI

tests/
├── unit/                # Unit tests with mocks
├── integration/         # Integration tests with real data
├── test_guidebook.py    # Guidebook constructor test
├── test_integration.py  # End-to-end test
└── test_*.py           # Other tests
```
