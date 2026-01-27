# Architecture Documentation

## Overview

The Help Ukraine Telegram Bot follows **Clean Architecture** principles with clear separation of concerns across four distinct layers. This architecture ensures testability, maintainability, and framework independence.

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
│  │  - Job scheduling                               │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │      TelegramAuthorizationAdapter               │   │
│  │  - Telegram admin checks                        │   │
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
│  │  - handle_social_reminder()                     │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │      AuthorizationService                       │   │
│  │  - is_admin_only_chat()                         │   │
│  │  - add_admin_only_chat()                        │   │
│  │  - remove_admin_only_chat()                     │   │
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
│  │  - IAuthorizationService                        │   │
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
3. **TelegramBotAdapter** → Checks access via `_check_access()`
   - Uses `AuthorizationService.is_admin_only_chat()`
   - If admin-only, uses `TelegramAuthorizationAdapter.is_user_admin()`
4. **BerlinHelpService** → Calls `handle_help()`
   - Formats multilingual help text
   - Uses `YamlGuidebook.format_results()`
5. **TelegramBotAdapter** → Sends reply via `_reply_to_message()`
   - Calls Telegram API to send message
   - Deletes original command message

## Key Principles

### 1. Dependency Inversion

All dependencies point inward toward the domain layer. Outer layers depend on protocols defined in inner layers, not on concrete implementations.

**Example:**
- `BerlinHelpService` depends on `IGuidebook` protocol, not `YamlGuidebook`
- `TelegramBotAdapter` depends on `IBerlinHelpService`, not `BerlinHelpService`

### 2. No Global State

All state is managed explicitly through dependency injection. No global variables or mutable singletons.

**Before (problematic):**
```python
# Global mutable state
ADMIN_ONLY_CHAT_IDS = [-1001723117571]
guidebook = Guidebook(...)

# Runtime mutation
ADMIN_ONLY_CHAT_IDS.append(chat_id)
```

**After (clean):**
```python
# Immutable dependency injection
auth_service = AuthorizationService(
    admin_only_chat_ids={-1001723117571}
)

# Explicit mutation through service
auth_service.add_admin_only_chat(chat_id)
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
- `authorization_service.py` - Access control rules

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
- `telegram_auth.py` - Telegram-specific authorization

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

    def get_info(self, topic: str) -> str:
        # Pure data access, no business logic
        return self._format_topic_info(self.guidebook.get(topic))
```

## Migration Patterns

### Pattern 1: Global State → Dependency Injection

**Before:**
```python
# Global mutable list
ADMIN_ONLY_CHAT_IDS = [-1001723117571]

# Mutated at runtime
ADMIN_ONLY_CHAT_IDS.append(chat_id)
```

**After:**
```python
# Service with encapsulated state
class AuthorizationService:
    def __init__(self, admin_only_chat_ids: Set[int]):
        self._admin_only_chat_ids = admin_only_chat_ids.copy()

    def add_admin_only_chat(self, chat_id: int):
        self._admin_only_chat_ids.add(chat_id)

# Injected in main.py
auth_service = AuthorizationService(
    admin_only_chat_ids={-1001723117571}
)
```

### Pattern 2: Decorator → Explicit Check

**Before:**
```python
@restricted
async def start_timer(update: Update, context: Context):
    # Decorator magically checks if user is admin
    ...
```

**After:**
```python
async def _handle_start_timer(self, update: Update, context: Context):
    # Explicit access check
    if not await self._check_admin_access(update, context):
        return
    ...
```

### Pattern 3: Tight Coupling → Protocol-Based Injection

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
        if not await self._check_access(update, context):
            return
        param = self._extract_parameter(update, "/newcommand")
        result = self.service.handle_new_command(param)
        await self._reply_to_message(update, context, result)
```

3. **Register handler:**
```python
def _register_handlers(self, application: Application):
    application.add_handler(CommandHandler("newcommand", self._handle_new_command))
```

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
