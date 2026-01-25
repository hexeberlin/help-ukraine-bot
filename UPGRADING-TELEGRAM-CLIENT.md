# Telegram Client Version Analysis

**Date:** 2026-01-23

## Current Version
**`python-telegram-bot==12.7`** (released ~2020)

Latest stable version: **21.11.1** (or 22.x in testing)

---

## Migration Scope: v12 → v21+

This is a **major migration** with fundamental architectural changes. The biggest breaking change happened in **v20.0** which rewrote the library to use `asyncio`.

### Key Breaking Changes

| Area | v12 (Current) | v20+ (Target) |
|------|---------------|---------------|
| **Callbacks** | `def callback(bot, update)` | `async def callback(update, context)` |
| **Entry point** | `Updater(TOKEN)` | `Application.builder().token(TOKEN).build()` |
| **Bot methods** | `bot.send_message(...)` | `await bot.send_message(...)` |
| **Filters** | `Filters.all` | `filters.ALL` (module, not class) |
| **JobQueue** | `context=chat_id` param | `data=chat_id` param |
| **Threading** | Thread-based | asyncio-based |

### Impact on This Codebase

**Files requiring changes:**

| File | Changes Needed |
|------|----------------|
| `src/main.py` | Replace `Updater` with `Application` builder pattern, change `Filters` to `filters` module |
| `src/commands.py` | Convert all 20+ handler functions to `async def`, add `await` to all bot method calls, update JobQueue API |
| `src/common.py` | Convert `send_results`, `delete_command`, `reply_to_message`, `restricted` decorator to async; fix `restricted` decorator signature inconsistency (see note below) |

### Specific Code Patterns to Change

**1. Handler signatures** (20+ functions in `commands.py`):
```python
# Current (v12)
def help_command(bot: Bot, update: Update):
    reply_to_message(bot, update, results)

# Required (v21)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply_to_message(update, context, results)
```

**2. Entry point** (`main.py:11-16`):
```python
# Current
updater = Updater(TOKEN)
dispatcher = updater.dispatcher

# Required
application = Application.builder().token(TOKEN).build()
```

**3. Job callbacks** (`commands.py:249-268`):
```python
# Current
def send_pinned_reminder(bot: Bot, job: Job):
    bot.forward_message(...)

# Required
async def send_pinned_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.forward_message(...)
```

**4. Filters** (`main.py:3,19`):
```python
# Current
from telegram.ext import Filters
MessageHandler(Filters.all, ...)

# Required
from telegram.ext import filters
MessageHandler(filters.ALL, ...)
```

**5. `restricted` decorator** (`common.py:63-79`):

⚠️ **Pre-existing issue:** The decorator wrapper uses `context: CallbackContext` parameter but decorated functions pass `update: Update`. This works because both have `effective_user` and `effective_chat` attributes, but the typing is inconsistent. Fix this during migration:
```python
# Current (inconsistent typing)
def wrapped(bot: Bot, context: CallbackContext, *args, **kwargs):
    user_id = context.effective_user.id  # works but typed as CallbackContext

# Required (v21 - also fixes typing)
async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
```

---

## Recommendation

| Option | Effort | Risk |
|--------|--------|------|
| **Stay on v12** | None | Security/compatibility debt accumulates; no new Telegram API features |
| **Upgrade to v13** | Low | Minimal changes; deprecated but more stable intermediate step |
| **Upgrade to v21+** | High | Full async rewrite; access to latest Bot API features |

**Suggested approach:** If upgrading, go directly to v21+ since v13-v19 are also deprecated. The async rewrite is unavoidable for long-term maintenance.

### Prerequisites for v21 Upgrade
1. Python 3.9+ required (currently using 3.11 per `runtime.txt` ✓)
2. Update all test mocks to handle async functions

---

## Sources
- [python-telegram-bot Changelog](https://docs.python-telegram-bot.org/changelog.html)
- [GitHub Releases](https://github.com/python-telegram-bot/python-telegram-bot/releases)
- [Transition Guide to v20.0](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Transition-guide-to-Version-20.0)
