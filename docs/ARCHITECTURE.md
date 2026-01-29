# Architecture Documentation

## Overview

The Help Ukraine Telegram Bot follows **Clean Architecture** principles with clear separation of concerns across four distinct layers. This architecture ensures testability, maintainability, and framework independence.

As of the statistics feature, guidebook requests are logged via a statistics service (SQLite in-memory) from the adapter layer, without leaking Telegram types into the application layer. Only topic-level statistics are retained.

## Layer Dependency Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Update                       │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              ADAPTER LAYER (Telegram-specific)          │
│  ┌─────────────────────────────────────────────────┐   │
│  │      TelegramBotAdapter                         │   │
│  │  - Handler registration                         │   │
│  │  - Command routing                              │   │
│  │  - Message formatting                           │   │
│  │  - Statistics logging                           │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │ Uses protocols from
                        ▼
┌─────────────────────────────────────────────────────────┐
│            APPLICATION LAYER (Business Logic)           │
│  ┌─────────────────────────────────────────────────┐   │
│  │      BerlinHelpService                          │   │
│  │  - handle_help()                                │   │
│  │  - handle_topic()                               │   │
│  │  - handle_cities()                              │   │
│  │  - handle_countries()                           │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │ Uses protocols from
                        ▼
┌─────────────────────────────────────────────────────────┐
│              DOMAIN LAYER (Protocols)                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Protocols (Interfaces)                         │   │
│  │  - IGuidebook                                   │   │
│  │  - IBerlinHelpService                           │   │
│  │  - IStatisticsService                           │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Models (Value Objects)                         │   │
│  │  - ChatContext                                  │   │
│  │  - CommandRequest                               │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────┘
                        │ Implemented by
                        ▼
┌─────────────────────────────────────────────────────────┐
│         INFRASTRUCTURE LAYER (External Systems)         │
│  ┌─────────────────────────────────────────────────┐   │
│  │      YamlGuidebook                              │   │
│  │  - Load YAML files                              │   │
│  │  - Format results                               │   │
│  │  - Vocabulary lookups                           │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │      StatisticsServiceSQLite                    │   │
│  │  - In-memory SQLite storage                     │   │
│  │  - Record guidebook requests                    │   │
│  │  - Purge old records (retention window)         │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │      ConfigLoader                               │   │
│  │  - load_env_config()                            │   │
│  │  - load_toml_settings()                         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Request Flow Example

**User sends `/help` command:**

1. **Telegram** → Update arrives at bot
2. **TelegramBotAdapter** → Routes to `_handle_help()` handler
3. **BerlinHelpService** → Calls `handle_help()`
   - Formats multilingual help text
   - Uses `YamlGuidebook.format_results()`
4. **TelegramBotAdapter** → Sends reply via `_reply_to_message()`
   - Calls Telegram API to send message
   - Deletes original command message

**User sends `/cities Berlin` command:**

1. **Telegram** → Update arrives at bot
2. **TelegramBotAdapter** → Routes to `_handle_cities()` handler
3. **TelegramBotAdapter** → Extracts "Berlin" parameter
4. **BerlinHelpService** → Calls `handle_cities("Berlin", show_all=False)`
5. **YamlGuidebook** → Returns formatted city information
6. **TelegramBotAdapter** → Records statistics via `IStatisticsService`
7. **TelegramBotAdapter** → Sends reply via `_reply_to_message()`

## Key Principles

### 1. Dependency Inversion

All dependencies point inward toward the domain layer. Outer layers depend on protocols defined in inner layers, not on concrete implementations.

**Example:**
- `BerlinHelpService` depends on `IGuidebook` protocol, not `YamlGuidebook`
- `TelegramBotAdapter` depends on `IBerlinHelpService`, not `BerlinHelpService`
- `TelegramBotAdapter` depends on `IStatisticsService`, not `StatisticsServiceSQLite`

### 2. No Global State

All state is managed explicitly through dependency injection. No global variables or mutable singletons.

**Before (problematic):**
```python
# Global mutable state
guidebook = Guidebook(...)
REMINDER_MESSAGE = "..."

# Direct global access
def handler():
    return guidebook.get_info(...)
```

**After (clean):**
```python
# Dependency injection
class TelegramBotAdapter:
    def __init__(self, service: IBerlinHelpService, guidebook: IGuidebook):
        self.service = service
        self.guidebook = guidebook
```

### 3. Framework Independence

Business logic has no knowledge of Telegram API. All Telegram-specific code is isolated in the adapter layer.

**Example:**
- `BerlinHelpService.handle_cities()` returns a string
- It doesn't know about `Update`, `Context`, or `Message` objects
- `TelegramBotAdapter` handles all Telegram API calls

### 4. Testability

Each layer can be tested independently:
- **Domain**: No tests needed (just protocols and value objects)
- **Application**: Test with mock guidebook
- **Adapter**: Test with mock services
- **Infrastructure**: Test with real YAML files

## Layer Responsibilities

### Domain Layer (`src/domain/`)

**Purpose:** Define the core business concepts and contracts

**Files:**
- `protocols.py` - Interface definitions (what operations are available)
- `models.py` - Immutable data structures

**Rules:**
- No dependencies on other layers
- No framework-specific code
- Only interfaces and value objects

### Application Layer (`src/application/`)

**Purpose:** Implement business logic and use cases

**Files:**
- `berlin_help_service.py` - Core help request handling logic

**Rules:**
- Depends only on domain protocols
- No Telegram types (Update, Context, etc.)
- Pure business logic
- Framework-agnostic

**Example:**
```python
class BerlinHelpService:
    def __init__(self, guidebook: IGuidebook):
        self.guidebook = guidebook

    def handle_cities(self, city_name: Optional[str], show_all: bool) -> str:
        if show_all:
            return self.guidebook.get_info("cities", name=None)
        return self.guidebook.get_cities(name=city_name)
```

### Adapter Layer (`src/adapters/`)

**Purpose:** Adapt external frameworks to work with our application

**Files:**
- `telegram_adapter.py` - Main bot adapter for python-telegram-bot

**Rules:**
- Depends on application services via protocols
- Contains all Telegram-specific code
- Translates between Telegram types and application types
- Handles async/await for Telegram API

**Example:**
```python
class TelegramBotAdapter:
    def __init__(self, service: IBerlinHelpService, ...):
        self.service = service

    async def _handle_cities(self, update: Update, context: Context):
        # Extract parameter from Telegram Update
        city_name = self._extract_parameter(update, "/cities")

        # Call business logic (framework-agnostic)
        result = self.service.handle_cities(city_name, show_all=False)

        # Send via Telegram API
        await self._reply_to_message(update, context, result)
```

### Infrastructure Layer (`src/infrastructure/`)

**Purpose:** Implement technical capabilities (database, file I/O, external APIs)

**Files:**
- `yaml_guidebook.py` - YAML file access
- `sqlite_statistics.py` - In-memory SQLite statistics storage
- `config_loader.py` - Configuration loading

**Rules:**
- Implements domain protocols
- Contains all I/O operations
- No business logic

**Example:**
```python
class YamlGuidebook:  # Implements IGuidebook protocol
    def __init__(self, guidebook_path: str, vocabulary_path: str):
        # Load from filesystem
        with open(guidebook_path, "r") as f:
            self.guidebook = safe_load(f)

    def get_info(self, group_name: str, name: Optional[str] = None) -> str:
        # Pure data access, no business logic
        return self._format_topic_info(self.guidebook.get(group_name), name=name)
```

## Statistics Logging

Guidebook requests initiated by users are recorded in memory:

- **What**: topic (key in `guidebook.yml`), topic description, timestamp
- **Where**: `StatisticsServiceSQLite` (in-memory SQLite DB)
- **When**: after command is processed, before reply is sent
- **Retention**: old records are purged on each insert (default 30 days)
- **Access**: Public command `/topic_stats [k]` returns top-k topics by request count

This keeps the logging concerns in the adapter + infrastructure layers and avoids leaking Telegram types into the application layer.

## Migration Patterns

**Before:**
```python
from src.guidebook import Guidebook

guidebook = Guidebook(...)  # Global instance

def cities_command(...):
    results = guidebook.get_cities(...)  # Direct dependency
```

**After:**
```python
class BerlinHelpService:
    def __init__(self, guidebook: IGuidebook):  # Protocol, not concrete
        self.guidebook = guidebook

    def handle_cities(self, city_name: str) -> str:
        return self.guidebook.get_cities(name=city_name)
```

### Pattern 2: Simplified Architecture

The project has evolved toward simplicity by removing features that added complexity without sufficient value:

**Removed features:**
- Authorization system (admin-only chats, access control)
- Reminder/scheduling system (pinned messages, social reminders)
- Related commands: `/start`, `/stop`, `/adminsonly`, `/adminsonly_revert`

**Result:**
- Simpler constructor: `TelegramBotAdapter` reduced from 12 to 4 parameters
- Fewer dependencies: No authorization service, no job scheduling
- Clearer focus: Bot provides information, no access control or automation
- All commands are public and accessible to anyone

## Benefits

### 1. Testability
- Each layer tested independently
- Mock dependencies easily with protocols
- Fast unit tests (no I/O, no network)

### 2. Flexibility
- Swap Telegram for Discord: Replace adapter layer only
- Change YAML to database: Replace infrastructure layer only
- Business logic unchanged

### 3. Maintainability
- Clear boundaries between layers
- Changes isolated to single layer
- Easy to understand request flow

### 4. Framework Independence
- Can upgrade python-telegram-bot without touching business logic
- Business logic reusable in other contexts
- No vendor lock-in

### 5. No Global State
- Predictable behavior
- Easy to test
- Thread-safe by design

## Testing Strategy

### Unit Tests (`tests/unit/`)

Test each component in isolation with mocks:

```python
# Test service with mock guidebook
def test_handle_cities(mock_guidebook):
    service = BerlinHelpService(guidebook=mock_guidebook)
    mock_guidebook.get_cities.return_value = "Berlin info"

    result = service.handle_cities("Berlin", show_all=False)

    assert result == "Berlin info"
    mock_guidebook.get_cities.assert_called_once_with(name="Berlin")
```

### Integration Tests (`tests/integration/`)

Test components working together with real dependencies:

```python
# Test service with real guidebook
def test_service_with_real_guidebook():
    guidebook = YamlGuidebook(
        guidebook_path="src/knowledgebase/guidebook.yml",
        vocabulary_path="src/knowledgebase/vocabulary.yml"
    )
    service = BerlinHelpService(guidebook=guidebook)

    result = service.handle_cities("Berlin", show_all=False)

    assert "Berlin" in result
```

### End-to-End Tests (`tests/test_integration.py`)

Test the entire system including Telegram framework:

```python
async def test_application_processes_help_command():
    # Build entire application with real dependencies
    adapter = TelegramBotAdapter(...)
    application = adapter.build_application()

    # Simulate Telegram Update
    update = Update(...)
    await application.process_update(update)

    # Verify response sent
    application.bot.send_message.assert_awaited()
```

## Common Patterns

### Adding a New Command

1. **Add business logic to service:**
```python
class BerlinHelpService:
    def handle_new_command(self, param: str) -> str:
        return self.guidebook.get_results(param)
```

2. **Add handler to adapter:**
```python
class TelegramBotAdapter:
    async def _handle_new_command(self, update: Update, context: Context):
        param = self._extract_parameter(update, "/newcommand")
        result = self.service.handle_new_command(param)
        await self._reply_to_message(update, context, result)
```

3. **Register handler:**
```python
def _register_handlers(self, application: Application):
    application.add_handler(CommandHandler("newcommand", self._handle_new_command))
```

### Available Commands

**Public Commands** (accessible to all users):
- `/help` - Display help text with available commands
- `/cities [name]` - Get information about a specific city
- `/cities_all` - List all available cities
- `/countries [name]` - Get information about a specific country
- `/countries_all` - List all available countries
- `/topic_*` - Dynamic handlers for all topics in guidebook.yml
- `/topic_stats [k]` - Top-k most requested topics (defaults to 10)

### Extending to New Platform (e.g., Discord)

1. Keep domain and application layers unchanged
2. Create new adapter: `src/adapters/discord_adapter.py`
3. Implement Discord-specific message handling
4. Use same `BerlinHelpService` for business logic

## Deployment Considerations

### Environment-Based Configuration

```python
def main():
    # Load config based on environment
    app_name, token, port = load_env_config()

    # Build application
    application = telegram_adapter.build_application()

    # Run mode based on APP_NAME
    if app_name == "TESTING":
        application.run_polling()  # Local dev
    else:
        application.run_webhook()  # Production (Heroku)
```

### Zero-Downtime Migration

The refactoring was done in phases:
1. Add new architecture (no changes to old code)
2. Add comprehensive tests for new architecture
3. Cut over main.py to use new architecture
4. Verify all tests pass
5. Remove old code

This ensured the old system worked until the new one was ready.

## Future Enhancements

### Potential Additions

1. **Database support**: Add `PostgresGuidebook` implementing `IGuidebook`
2. **Caching layer**: Wrap guidebook with caching decorator
3. **Analytics service**: Track command usage via new service
4. **Multi-language support**: Add `ITranslationService` protocol
5. **Discord adapter**: Support multiple platforms

All additions follow the same pattern:
- Define protocol in domain layer
- Implement in appropriate layer
- Inject via `main.py`
- No changes to existing code

## Conclusion

This architecture provides a solid foundation for long-term maintainability and extensibility. The clear separation of concerns, dependency inversion, and protocol-based design make it easy to:

- Test each component independently
- Swap implementations without breaking changes
- Add new features without touching existing code
- Migrate to different frameworks or platforms

The initial investment in proper architecture pays dividends in reduced bugs, faster development, and easier onboarding of new contributors.
