# Clean Architecture Refactoring Plan

## Overview

Transform the Telegram bot into a Clean Architecture design with clear separation between business logic and framework:

```
Domain Layer (Protocols) → Application Layer (Services) → Adapter Layer (Telegram) → Infrastructure (YAML)
```

## Architecture Layers

### 1. Domain Layer (`src/domain/`)
**Abstract interfaces using Protocol (structural typing)**

```python
# protocols.py
class IGuidebook(Protocol):
    def get_info(group_name: str, name: Optional[str]) -> str: ...
    def get_cities(name: Optional[str]) -> str: ...
    def get_countries(name: Optional[str]) -> str: ...
    def get_topics() -> List[str]: ...
    def get_descriptions() -> Dict[str, str]: ...

class IBerlinHelpService(Protocol):
    def handle_help() -> str: ...
    def handle_topic(topic_name: str) -> str: ...
    def handle_cities(city_name: Optional[str], show_all: bool) -> str: ...
    def handle_countries(country_name: Optional[str], show_all: bool) -> str: ...
    def handle_social_reminder() -> str: ...

# models.py - Lightweight value objects
@dataclass(frozen=True)
class ChatContext:
    chat_id: int
    user_id: int
    is_admin: bool = False
```

### 2. Application Layer (`src/application/`)
**Business logic independent of Telegram**

```python
# berlin_help_service.py
class BerlinHelpService(IBerlinHelpService):
    def __init__(self, guidebook: IGuidebook):
        self._guidebook = guidebook

    def handle_help() -> str:
        # Extract from commands.help_text()
        return self._guidebook.format_results(help_text)

    def handle_topic(topic_name: str) -> str:
        info = self._guidebook.get_info(group_name=topic_name)
        return f"#{topic_name}\n{info}"

    # ... other handlers

# authorization.py
class AuthorizationService:
    def __init__(self, admin_only_chat_ids: Set[int]):
        self._admin_only_chat_ids = admin_only_chat_ids

    def is_admin_only_chat(chat_id: int) -> bool: ...
    def add_admin_only_chat(chat_id: int) -> None: ...
    def remove_admin_only_chat(chat_id: int) -> None: ...
```

### 3. Infrastructure Layer (`src/infrastructure/`)
**Concrete implementations**

```python
# yaml_guidebook.py
class YamlGuidebook(IGuidebook):
    """Move current Guidebook class here unchanged"""
    def __init__(self, guidebook_path: str, vocabulary_path: str):
        # Current implementation from guidebook.py
        ...
```

### 4. Adapter Layer (`src/adapters/`)
**Telegram framework binding**

```python
# telegram_adapter.py
class TelegramBotAdapter:
    def __init__(
        self,
        token: str,
        service: IBerlinHelpService,
        guidebook_topics: List[str],
        guidebook_descriptions: Dict[str, str],
        auth_service: AuthorizationService,
        telegram_auth: TelegramAuthorizationAdapter,
        # ... config
    ):
        self._service = service
        # ...

    def build_application() -> Application:
        """Create PTB Application and register handlers"""
        self._application = Application.builder().token(self._token).build()
        self._register_handlers()
        return self._application

    def _register_handlers():
        """Register command handlers that delegate to service"""
        app.add_handler(CommandHandler("help", self._handle_help))
        # Dynamic topic handlers
        for topic in self._guidebook_topics:
            if topic not in {"cities", "countries"}:
                app.add_handler(CommandHandler(topic, self._create_topic_handler(topic)))
        # ... etc

    async def _handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        result = self._service.handle_help()
        await self._reply_to_message(update, context, result)

    # Helper methods: _extract_parameter, _reply_to_message, _delete_command, etc.

# telegram_auth.py
class TelegramAuthorizationAdapter:
    async def is_user_admin(user_id: int, chat_id: int, bot: Bot) -> bool:
        """Call Telegram API to check admin status"""
        admins = await bot.get_chat_administrators(chat_id=chat_id)
        return user_id in [member.user.id for member in admins]
```

### 5. Main Entry Point (`src/main.py`)
**Dependency injection and bootstrap**

```python
def main() -> None:
    # Load configuration
    settings = load_settings("settings.toml")

    # Create concrete implementations (Infrastructure)
    guidebook = YamlGuidebook(
        guidebook_path=settings["GUIDEBOOK_PATH"],
        vocabulary_path=settings["VOCABULARY_PATH"]
    )

    # Create services (Application)
    berlin_help_service = BerlinHelpService(guidebook=guidebook)
    auth_service = AuthorizationService(admin_only_chat_ids=set(ADMIN_ONLY_CHAT_IDS))

    # Create adapters (Adapter)
    telegram_auth = TelegramAuthorizationAdapter()
    telegram_adapter = TelegramBotAdapter(
        token=TOKEN,
        service=berlin_help_service,
        guidebook_topics=guidebook.get_topics(),
        guidebook_descriptions=guidebook.get_descriptions(),
        auth_service=auth_service,
        telegram_auth=telegram_auth,
        berlin_chat_ids=BERLIN_HELPS_UKRAINE_CHAT_ID,
        reminder_config={...}
    )

    # Build and run
    application = telegram_adapter.build_application()

    if APP_NAME == "TESTING":
        application.run_polling()
    else:
        application.run_webhook(...)
```

## File Structure

```
src/
├── domain/
│   ├── __init__.py
│   ├── protocols.py          # IGuidebook, IBerlinHelpService, IAuthorizationService
│   ├── models.py             # ChatContext, CommandRequest (value objects)
│   └── exceptions.py         # Domain exceptions
│
├── application/
│   ├── __init__.py
│   ├── berlin_help_service.py  # Core business logic
│   └── authorization.py        # Authorization service
│
├── infrastructure/
│   ├── __init__.py
│   ├── yaml_guidebook.py      # YamlGuidebook (from current guidebook.py)
│   └── config_loader.py       # Load settings.toml
│
├── adapters/
│   ├── __init__.py
│   ├── telegram_adapter.py    # TelegramBotAdapter
│   └── telegram_auth.py       # TelegramAuthorizationAdapter
│
├── main.py                    # Entry point with DI
└── knowledgebase/            # (unchanged)

tests/
├── unit/
│   ├── test_berlin_help_service.py
│   ├── test_yaml_guidebook.py
│   └── test_telegram_adapter.py
├── integration/
│   └── test_bot_integration.py
└── conftest.py
```

## Key Design Decisions

1. **Use Protocol over ABC**: Structural typing, more Pythonic, easier testing
2. **Eliminate @restricted decorator**: Replace with explicit `await self._check_admin_access()`
3. **Value objects for data**: `@dataclass(frozen=True)` for ChatContext, etc.
4. **Two-layer authorization**:
   - Domain: AuthorizationService (business rules)
   - Adapter: TelegramAuthorizationAdapter (Telegram API calls)
5. **Adapter encapsulates Telegram**: Update/Context never leak to domain/application

## Testing Strategy

### Unit Tests with Mocks

#### Test BerlinHelpService (mock Guidebook)
```python
@pytest.fixture
def mock_guidebook():
    mock = Mock(spec=IGuidebook)
    mock.format_results.side_effect = lambda x: f"==={x}==="
    mock.get_info.return_value = "Test info"
    return mock

def test_handle_topic_prefixes_with_hashtag(service, mock_guidebook):
    result = service.handle_topic("accommodation")
    assert result == "#accommodation\nTest info"
    mock_guidebook.get_info.assert_called_once_with(group_name="accommodation")
```

#### Test TelegramAdapter (mock Service)
```python
@pytest.fixture
def mock_service():
    mock = Mock(spec=IBerlinHelpService)
    mock.handle_help.return_value = "Help text"
    mock.handle_cities.return_value = "Cities info"
    return mock

@pytest.mark.anyio
async def test_handle_help_calls_service(adapter, mock_service):
    update = SimpleNamespace(effective_message=...)
    context = SimpleNamespace(bot=AsyncMock())

    await adapter._handle_help(update, context)

    mock_service.handle_help.assert_called_once()
    context.bot.send_message.assert_awaited()
```

#### Test YamlGuidebook (real YAML files)
```python
def test_get_info_returns_formatted_string(guidebook):
    result = guidebook.get_info("accommodation")
    assert isinstance(result, str)
    assert len(result) > 0
```

### Integration Tests
```python
def test_service_with_real_guidebook(real_service):
    """Integration test using real YAML data"""
    result = real_service.handle_topic("accommodation")
    assert "#accommodation" in result
```

## Migration Path (6 Phases)

### Phase 1: Domain & Infrastructure (No Breaking Changes)
- Create `src/domain/` with protocols.py, models.py
- Create `src/infrastructure/` with yaml_guidebook.py
- Copy Guidebook → YamlGuidebook
- Write unit tests for YamlGuidebook
- **Risk: Zero** (purely additive)

### Phase 2: Application Layer
- Create `src/application/` with berlin_help_service.py
- Extract business logic from commands.py
- Create authorization.py
- Write unit tests with mocked guidebook
- **Risk: Low** (parallel implementation)

### Phase 3: Adapter Layer
- Create `src/adapters/` with telegram_adapter.py
- Move handler registration from commands.py
- Create telegram_auth.py
- Write tests with mocked service
- **Risk: Medium** (complex adapter)

### Phase 4: Refactor main.py (Cutover)
- Rewrite main.py with dependency injection
- Update imports
- Run full test suite
- **Risk: High** (cutover point)

### Phase 5: Remove Legacy Code
- Delete src/guidebook.py, src/commands.py, src/common.py
- Update all tests
- **Risk: Low** (if Phase 4 succeeded)

### Phase 6: Documentation
- Update CLAUDE.md
- Add architecture diagrams
- Document testing approach

## Critical Files

### To Extract/Refactor
1. `src/guidebook.py` → infrastructure/yaml_guidebook.py
2. `src/commands.py` → Split:
   - Business logic → application/berlin_help_service.py
   - Telegram handlers → adapters/telegram_adapter.py
3. `src/common.py` → Distribute:
   - send_results, reply_to_message → adapters/telegram_adapter.py
   - @restricted logic → adapters/telegram_auth.py

### To Rewrite
4. `src/main.py` → Dependency injection pattern

### Test Patterns
5. `tests/test_commands.py` → Adapt for new architecture

## Verification

### End-to-End Testing
1. **Unit tests pass**: `pytest tests/unit/`
2. **Integration tests pass**: `pytest tests/integration/`
3. **Manual testing**:
   - Start bot in TESTING mode: `python -m src.main`
   - Test commands: `/help`, `/cities berlin`, `/accommodation`
   - Verify admin commands work
4. **Existing tests pass**: `pytest tests/`
5. **Lint passes**: `pylint -E src tests`

### Functionality Checklist
- [ ] Help command works
- [ ] Dynamic topic commands work (accommodation, animals, etc.)
- [ ] Cities command with parameter works
- [ ] Countries command works
- [ ] Admin-only commands restricted properly
- [ ] Reminder system functions
- [ ] Message deletion works
- [ ] Greeting deletion works

## Benefits

1. **Testability**: Mock simple interfaces vs complex Telegram objects
2. **Flexibility**: Easy to add Discord/Slack adapters
3. **Clarity**: Clear layer separation
4. **Maintainability**: Changes isolated to single layer
5. **Independent evolution**: Upgrade PTB without touching business logic
