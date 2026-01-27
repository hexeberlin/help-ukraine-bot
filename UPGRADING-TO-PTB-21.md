# Plan: Upgrade to python-telegram-bot 21.x

## 1. Lock Target Release
- Pin `python-telegram-bot==21.11.*` in `requirements.txt` and drop obsolete dependencies (`future`, `tornado`, `decorator`, `schedule`) that were only needed by older PTB releases.
- Regenerate the dependency lock (`pip freeze` snapshot used during deploys) and run `pip check` to ensure no transitive dependency still expects the old PTB stack.
- Add a smoke test (e.g., `tests/test_deps.py`) that imports PTB and key modules to catch missing wheels early and keep it in CI.
- Confirm Python 3.11 (already set in `runtime.txt`) is sufficient for PTB 21.

## 2. Rebuild the Entry Point (`src/main.py`)
- Replace `Updater`/`Dispatcher` usage with `Application.builder().token(TOKEN).build()` and migrate `Filters` imports to the `telegram.ext.filters` module.
- Refactor `main()` into an async-aware bootstrap: register handlers via a new `commands.register(application)` helper, attach a `post_init` coroutine that sets bot commands, and switch to `Application.run_polling()` / `run_webhook(...)`.
- Update the webhook path to await `set_webhook` and verify the Heroku `Procfile` continues to run `python -m src.main` (now wrapping `asyncio.run(main())` if needed).
- Add an integration test that instantiates the `Application` in a test event loop, ensures handlers register without hitting Telegram, and asserts `set_my_commands` is scheduled (use `AsyncMock` for bot).

## 3. Async-ify Shared Helpers (`src/common.py`)
- Convert `send_results`, `reply_to_message`, and `delete_command` to `async def` functions and await `context.bot` calls throughout.
- Update the `restricted` decorator to accept `(update, context)` and support async handlers by awaiting the wrapped coroutine; pull admin IDs via `await context.bot.get_chat_administrators(chat_id)`.
- Simplify `get_param` to use `(update, command)` since handlers now access the bot via `context`.
- Add unit tests that call each helper/decorator via `pytest.mark.asyncio` with mocked `context.bot`, covering both success paths and error handling (e.g., `BadRequest` in `delete_command`).

## 4. Refactor Command Handlers (`src/commands.py`)
- Change every handler signature to `async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE)` and move direct bot interactions to `context.bot`.
- Replace `add_commands` with a `register(application: Application)` helper that adds handlers directly (no return value).
- Update helper calls (`send_results`, `reply_to_message`, etc.) to be awaited; adjust the `build_handler` closures accordingly.
- Convert `delete_greetings` to async and keep using `effective_message_type` for filtering join/leave events.
- Expand the test suite with async handler tests that assert replies contain expected strings (`/help`, `/cities`, etc.) and that restricted commands reject non-admins (mocking admin lists).

## 5. Rework JobQueue Usage
- Stop importing `schedule.Job`; rely on PTB’s `telegram.ext.Job` and the job queue attached to each context.
- Remove `pass_job_queue=True` arguments; obtain the job queue inside handlers via `context.job_queue`.
- Update job callbacks (`send_pinned_reminder`, `send_social_reminder`) to async coroutines that receive a single `ContextTypes.DEFAULT_TYPE` argument, use `context.job` / `context.data` for chat IDs, and await bot calls.
- Ensure job names (`PINNED_JOB`, `SOCIAL_JOB`) continue to scope reminders per chat, possibly by storing chat IDs in job data if multiple chats schedule jobs simultaneously.
- Create scheduler-focused tests that enqueue fake jobs via `application.job_queue`, advance the test clock (using PTB’s `application.create_task` helpers or `freezegun`), and assert reminders send the correct messages.

## 6. Update Tests and Tooling
- Convert tests that call handlers directly to async tests (`pytest.mark.asyncio`) or drive them via `asyncio.run`.
- Add coverage for the new async helper/decorator behavior and the JobQueue logic (mock `ContextTypes` and admin lookups).
- Run `pytest`, `pylint`, and (optionally) `mypy` in CI to ensure async conversions didn’t regress behavior; gate merges on these checks.

## 7. Document and Roll Out
- Extend `README.md` / `UPGRADING-TELEGRAM-CLIENT.md` with a migration summary (async rewrite, dependency changes, operational considerations).
- Update deployment runbooks to reflect webhook vs polling behavior with PTB 21.
- After merging, deploy to staging, run end-to-end smoke tests (sending sample commands and verifying reminders), monitor for asyncio runtime warnings, then promote to production.

---

## Status Snapshot (2026-01-26)

### ✅ Completed
- Requirements now pin PTB `21.11` and the repo installs cleanly via `pip check`.
- `src/common.py`, `src/commands.py`, and `src/main.py` have been fully ported to the async API (Application builder, async helpers, new JobQueue usage).
- Added regression tests (`tests/test_common.py`, `tests/test_commands.py`, `tests/test_deps.py`, `tests/test_integration.py`) covering async helpers, scheduling logic, dependency versioning, and end-to-end Application behavior; `pytest` passes in CI.
- Documentation updated in `CLAUDE.md`, `README.md`, and `UPGRADING-TELEGRAM-CLIENT.md` to reflect the new architecture.
- Merged to master (PR #184, commit da8ed99) on 2026-01-26.
- Successfully deployed to production and test environments via automatic deployment pipeline.

### 📝 Optional Future Work
- Consider upgrading to PTB 22.x for Bot API 7.10 features.
- Address existing pylint docstring/style warnings if desired (unchanged from pre-upgrade).
