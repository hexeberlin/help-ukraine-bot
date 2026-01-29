# Plan: Remove Reminder Logic and Admin Authorization Layer

## Overview

Remove two major features from the Help Ukraine Bot:
1. **Reminder Logic** - Scheduled jobs for pinned messages and social help reminders
2. **Admin Authorization Layer** - Complete access control system including admin-only chats

Both features are cleanly separated across architectural layers and can be removed while maintaining system integrity.

## Files to Delete

- `src/application/authorization_service.py`
- `src/adapters/telegram_auth.py`
- `tests/unit/test_authorization_service.py`

## Files to Modify

### Domain Layer
- `src/domain/protocols.py`
  - Remove `IAuthorizationService` protocol (lines 66-83)
  - Remove `handle_social_reminder()` from `IBerlinHelpService` (lines 61-63)

### Application Layer
- `src/application/berlin_help_service.py`
  - Remove `handle_social_reminder()` method (lines 108-115)

### Adapter Layer
- `src/adapters/telegram_adapter.py` (largest change - ~400 lines removed)
  - Remove imports: `IAuthorizationService`, `TelegramAuthorizationAdapter`, `Job`, `JobQueue`
  - Remove 8 constructor parameters (auth services + reminder config)
  - Remove 4 handler registrations: `/start`, `/stop`, `/adminsonly`, `/adminsonly_revert`
  - Remove 11 methods:
    - Handler methods: `_handle_start_timer()`, `_handle_stop_timer()`, `_handle_admins_only()`, `_handle_admins_only_revert()`
    - Auth methods: `_check_access()`, `_check_admin_access()`
    - Reminder methods: `_start_reminder()`, `_add_pinned_reminder_job()`, `_add_info_job()`, `_send_pinned_reminder()`, `_send_social_reminder()`, `_job_name()`, `_chat_jobs()`
  - Remove `_check_access()` calls from public command handlers (6 locations)

### Entry Point
- `src/main.py`
  - Remove imports for `AuthorizationService` and `TelegramAuthorizationAdapter`
  - Remove service instantiations
  - Remove 8 parameters from `TelegramBotAdapter` constructor call

### Config
- `src/config.py`
  - Remove deprecated constants: `REMINDER_MESSAGE`, `REMINDER_INTERVAL_*`, `*_JOB`, `ADMIN_ONLY_CHAT_IDS`, `BERLIN_HELPS_UKRAINE_CHAT_ID`

### Tests
- `tests/unit/test_telegram_adapter.py`
  - Remove `mock_auth_service` and `mock_telegram_auth` fixtures
  - Update `adapter` fixture to remove auth/reminder parameters
  - Remove 10 test methods related to auth and reminders
- `tests/unit/test_berlin_help_service.py`
  - Remove `test_handle_social_reminder`
- `tests/test_integration.py`
  - Update adapter instantiation to remove auth/reminder parameters

## Implementation Sequence

Follow Clean Architecture layers from inside-out:

1. **Domain Layer** - Remove protocols from `src/domain/protocols.py`
2. **Application Layer** - Delete `authorization_service.py`, update `berlin_help_service.py`
3. **Adapter Layer** - Delete `telegram_auth.py`, update `telegram_adapter.py` (largest change)
4. **Entry Point** - Update `main.py` and `config.py`
5. **Tests** - Delete auth test file, update remaining tests

## Behavioral Changes

**Public Commands** (currently have auth checks, will become fully public):
- `/help`, `/cities`, `/cities_all`, `/countries`, `/countries_all`, `/topic_*` commands

**Removed Commands** (will return "unknown command"):
- `/start` (start reminders)
- `/stop` (stop reminders)
- `/adminsonly` (restrict chat to admins)
- `/adminsonly_revert` (remove admin restriction)

**No Breaking Changes**:
- All existing public commands continue to work
- No changes to guidebook.yml structure
- No changes to external APIs or dependencies

## Verification Plan

### 1. Static Analysis
```bash
uv run pylint -E src tests
```
Should report no errors.

### 2. Test Suite
```bash
uv run pytest tests -v
```
All remaining tests should pass.

### 3. Grep Verification
```bash
grep -r "AuthorizationService\|TelegramAuthorizationAdapter\|handle_social_reminder\|_check_access\|start_reminder" src/
```
Should return no results (except possibly in comments).

### 4. Manual Testing
```bash
uv run python -m src.main
```
Test commands:
- `/help` - should work without auth checks
- `/cities Berlin` - should return city info
- `/topic_stats` - should show stats
- `/start`, `/stop`, `/adminsonly` - should be unrecognized

## Critical Files

- `src/adapters/telegram_adapter.py` - Most complex changes (~400 lines removed)
- `src/domain/protocols.py` - Foundation changes (protocol removal)
- `src/main.py` - Dependency injection updates
- `tests/unit/test_telegram_adapter.py` - Most test changes

## Architecture Benefits

- **Simplified adapter**: Constructor reduced from 10 to 3 parameters
- **Reduced complexity**: 11 methods and ~400 lines removed from telegram_adapter.py
- **Cleaner contracts**: Focused service layer without access control logic
- **Better performance**: No background jobs or periodic API calls
- **3 fewer files** in codebase

## Post-Implementation Tasks

After successful implementation and verification:
1. Update CLAUDE.md to remove documentation about authorization and reminder features
2. Optionally remove unused 'social_help' topic from guidebook.yml (harmless if left)
