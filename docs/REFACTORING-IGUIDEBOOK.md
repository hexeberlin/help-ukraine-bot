# Refactoring Plan: `IGuidebook`

This document captures the proposed simplification of the `IGuidebook` protocol and the corresponding changes needed across the codebase.

## Current State

- `guidebook.yml` entries follow a `description` + `contents` schema. The exceptions are `cities` and `countries`, whose `contents` hold nested dictionaries keyed by city/country names.
- `YamlGuidebook` splits YAML data into `self.guidebook` (contents only) and `self.descriptions`, exposing formatting-oriented methods (`get_info`, `get_results`, `format_results`) in the protocol.
- Consumers mostly require topic metadata:
  - `BerlinHelpService` uses `get_results`/`format_results` to serve topic content and only calls `get_info` to render “all cities/countries”.
  - `TelegramBotAdapter` relies on `get_topics`, `get_descriptions`, and the special `get_cities`/`get_countries` helpers.

## Target API

Keep the specialized `get_cities`/`get_countries` methods, but reduce the generic API to:

1. `get_topics() -> list[str]`
2. `get_topic_description(topic: str) -> Optional[str]`
3. `get_topic_contents(topic: str) -> GuidebookContent` (where `GuidebookContent` covers both list and dict payloads)

Formatting moves out of the guidebook interface.

## Implementation Steps

1. **Update `IGuidebook` (`src/domain/protocols.py`)**
   - Remove `get_info`, `get_results`, `get_descriptions`, and `format_results`.
   - Add the `get_topic_description` and `get_topic_contents` methods (plus a type alias for contents if helpful).
   - Document that formatting is handled by higher layers.

2. **Refine `YamlGuidebook` (`src/infrastructure/yaml_guidebook.py`)**
   - Store each topic as a struct/dict containing both description and contents so single-topic lookups are straightforward.
   - Implement the two new getters with case-insensitive matching and reuse the existing lowercase cache for nested dictionaries.
   - Keep `get_cities`/`get_countries` for parameterized lookups, but expose `get_topic_contents("cities")`/`("countries")` so callers can render the full lists without `get_info`.
   - Drop the public formatting helpers.

3. **Introduce a shared formatter (e.g., `src/application/guidebook_formatter.py`)**
   - Provide `format_contents(contents, title=None)` and `wrap_with_separator(text)` so services/adapters can reproduce the current separators and per-section rendering.
   - Cover the formatter with unit tests (list vs. dict content, optional headings).

4. **Adjust `BerlinHelpService` (`src/application/berlin_help_service.py`)**
   - Replace `guidebook.format_results`/`get_results` with the formatter + `get_topic_contents`.
   - Fetch descriptions when helpful (e.g., prepend to topic responses or reuse in stats later).
   - When handling `/cities_all` or `/countries_all`, use `get_topic_contents` instead of `get_info`.

5. **Update `TelegramBotAdapter` (`src/adapters/telegram_adapter.py`)**
   - Build command handlers using `get_topics` as today.
   - Fetch per-topic descriptions via `get_topic_description(topic)` when creating `BotCommand` objects and when recording statistics.
   - Optional optimization: cache descriptions locally to avoid multiple lookups in `_bot_commands` and `_record_stats`.

6. **Revise tests**
   - `tests/unit/test_yaml_guidebook.py`: verify the new getters and keep coverage for `get_cities`/`get_countries`.
   - `tests/unit/test_berlin_help_service.py` + integration tests: ensure the service uses the formatter and still renders separators/hashtags.
   - `tests/unit/test_telegram_adapter.py`: mock the updated interface (`get_topic_description`) and ensure stats logging/command registration work.
   - Add formatter tests covering dict/list rendering and separator logic.

7. **Run CI locally**
   - Execute `uv run pytest` after the refactor to confirm behavior parity.

## Removing `TelegramBotAdapter`'s Guidebook Dependency

The adapter currently imports `IGuidebook` to (a) enumerate topics for handler registration, (b) build `BotCommand`s with human-readable descriptions, and (c) look up descriptions while recording statistics (`src/adapters/telegram_adapter.py:109-422`). All of that information already flows through `BerlinHelpService` via its injected guidebook, so we can keep the adapter unaware of guidebook details by expanding the service contract:

1. **Extend `IBerlinHelpService`**
   - Add read-only topic metadata methods such as `list_topics() -> list[str]` and `get_topic_description(topic: str) -> Optional[str]`. These simply delegate to the guidebook implementation.
   - Optionally introduce a `TopicMeta` dataclass (name + description) if returning paired metadata is more convenient for command registration.

2. **Update `BerlinHelpService`**
   - Implement the new metadata methods by calling `get_topics`/`get_topic_description` on the guidebook.
   - Consider caching the list/description pair to avoid re-reading from YAML on every adapter call, especially when `_bot_commands()` iterates over topics more than once.

3. **Refactor `TelegramBotAdapter`**
   - Drop the `guidebook: IGuidebook` constructor parameter. Use `service.list_topics()` for handler registration and `service.get_topic_description()` (or `TopicMeta`) when building the `/help` command list and while logging statistics.
   - Ensure `_record_stats` continues to send a description string to `IStatisticsService` by fetching it from the service.

4. **Adjust Composition & Tests**
   - Remove the guidebook argument when constructing `TelegramBotAdapter` in `main.py`; only the service retains the dependency.
   - Update unit tests that mocked `guidebook` inside the adapter—mocks now live on the service methods instead.

With this change the adapter talks exclusively to `IBerlinHelpService`, keeping the I/O layer ignorant of the domain data source while the service remains the single consumer of `IGuidebook`.
