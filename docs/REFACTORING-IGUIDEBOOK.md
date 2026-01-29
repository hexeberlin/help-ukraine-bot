# Refactoring Plan: `IGuidebook`

This document captures the proposed simplification of the `IGuidebook` protocol and the corresponding changes needed across the codebase.

**Status**: This plan was created after commit 7eb3256 (Jan 27, 2026) which introduced the guidebook dependency to `TelegramBotAdapter`. The auth/reminder removal (commit 494095c, Jan 29, 2026) has been completed separately. This refactoring is not yet implemented.

## Terminology

To ensure clarity and consistency, this document uses the following terminology when referring to the structure of `src/knowledgebase/guidebook.yml`:

- **Topic**: A root-level key in `guidebook.yml` (e.g., `accommodation`, `cities`, `apartment_approval`)
- **Topic description**: The value of the `description` key within a topic entry (e.g., "Поиск временного жилья")
- **Contents**: The value of the `contents` key within a topic entry. Can be:
  - A list of strings (e.g., `apartment_approval`)
  - A dictionary mapping keys to lists (e.g., `animals`, `cities`, `countries`)
  - For most topics, contents are treated as a single, non-splittable unit regardless of internal structure
- **Subtopic**: **Only applicable to `cities` and `countries` topics** - these are separately addressable keys within the contents dictionary:
  - For `cities`: city names like "Berlin", "Munich" (accessed via `/cities Berlin`)
  - For `countries`: country names like "Poland", "Austria" (accessed via `/countries Poland`)
  - All other topics do NOT have subtopics, even if their contents is a dict with section headers

### Validation Against `guidebook.yml`

Example topic with list contents (non-splittable):
```yaml
apartment_approval:
  description: Процесс одобрения квартиры Jobcenter  # ← topic description
  contents:  # ← contents (list, treated as single unit)
    - "Item 1..."
    - "Item 2..."
```

Example topic with dict contents (non-splittable):
```yaml
animals:
  description: Помощь домашним животным  # ← topic description
  contents:  # ← contents (dict, but treated as single unit - NO subtopics)
    Полезные ссылки:  # ← section header (NOT a subtopic)
      - https://tasso.net
      - https://linktr.ee/support_ukrainian_pets
    Бесплатная помощь животным беженцев:  # ← section header (NOT a subtopic)
      - https://hundedoc-berlin.de
```

Example topic with subtopics (separately addressable):
```yaml
cities:
  description: Чаты по городам Германии (введите /cities ГОРОД)  # ← topic description
  contents:  # ← contents (dict with subtopics)
    Berlin:  # ← SUBTOPIC (city name - separately addressable via /cities Berlin)
      - https://t.me/berlinhelpsukrainians
      - https://t.me/ukrainehelpberlin
    Munich:  # ← SUBTOPIC (city name - separately addressable via /cities Munich)
      - https://t.me/munichhilft
```

## Current State

- All topics in `guidebook.yml` follow a consistent schema: each topic has a `description` field (the topic description) and a `contents` field (the contents, which can be a list or dict).
- `YamlGuidebook` splits YAML data into `self.guidebook` (contents only) and `self.descriptions` (topic descriptions only), exposing formatting-oriented methods (`get_info`, `get_results`, `format_results`) in the protocol.
- Consumers mostly require topic metadata:
  - `BerlinHelpService` uses `get_results`/`format_results` to serve contents and only calls `get_info` to render "all cities/countries" (all subtopics for the `cities`/`countries` topics).
  - `TelegramBotAdapter` relies on `get_topics`, `get_descriptions`, and the special `get_cities`/`get_countries` helpers for parameterized queries (e.g., `/cities Berlin`).

## Target API

Keep the specialized `get_cities`/`get_countries` methods for parameterized queries (e.g., `/cities Berlin` to get a specific city's subtopic), but reduce the generic API to:

1. `get_topics() -> list[str]` — Returns all topic names
2. `get_topic_description(topic: str) -> Optional[str]` — Returns the topic description for a given topic
3. `get_topic_contents(topic: str) -> GuidebookContent` — Returns the entire contents for a given topic as a single unit (where `GuidebookContent` covers both list and dict payloads)

Notes:
- `get_topic_contents("cities")` returns the full dict of all cities (all subtopics)
- `get_cities(name="Berlin")` returns only Berlin's content (single subtopic lookup)
- For all other topics, contents are treated as single, non-splittable units

Formatting moves out of the guidebook interface into a separate formatter module.

## Implementation Steps

1. **Update `IGuidebook` (`src/domain/protocols.py`)**
   - Remove `get_info`, `get_results`, `get_descriptions`, and `format_results`.
   - Add `get_topic_description(topic: str) -> Optional[str]` to retrieve a topic description.
   - Add `get_topic_contents(topic: str) -> GuidebookContent` to retrieve contents (define `GuidebookContent = Union[List[str], Dict[str, List[str]]]` type alias).
   - Keep `get_cities` and `get_countries` for parameterized subtopic lookups.
   - Document that formatting is handled by higher layers.

2. **Refine `YamlGuidebook` (`src/infrastructure/yaml_guidebook.py`)**
   - Store each topic as a struct/dict containing both topic description and contents together (instead of splitting into separate `self.guidebook` and `self.descriptions` dicts).
   - Implement `get_topic_description()` and `get_topic_contents()` with case-insensitive topic name matching.
   - Reuse the existing lowercase cache for subtopic lookups **only for `cities` and `countries` topics** (case-insensitive matching of city/country names).
   - Keep `get_cities(name)` and `get_countries(name)` for parameterized subtopic lookups with vocabulary alias support.
   - Expose `get_topic_contents("cities")` and `get_topic_contents("countries")` so callers can retrieve all cities/countries (all subtopics) when needed.
   - Drop the public formatting helpers (`format_results`, static method).

3. **Introduce a shared formatter (e.g., `src/application/guidebook_formatter.py`)**
   - Provide `format_contents(contents: GuidebookContent, title: Optional[str] = None) -> str` to format contents (handles both list and dict structures).
   - Provide `wrap_with_separator(text: str) -> str` to add the `"=" * 30` separator lines.
   - For dict-based contents, format each key as a section header with its corresponding list items as bullet points (applies to both topics like `animals` with section headers, and `cities`/`countries` with subtopics).
   - For list-based contents, format as simple newline-separated items.
   - Cover the formatter with unit tests (list vs. dict contents, optional title parameter, section header rendering).

4. **Adjust `BerlinHelpService` (`src/application/berlin_help_service.py`)**
   - Replace `guidebook.format_results(help_text)` with `formatter.wrap_with_separator(help_text)`.
   - Replace `guidebook.get_results(topic)` with `formatter.format_contents(guidebook.get_topic_contents(topic))`.
   - Preserve the `#{topic_name}\n` prefix in `handle_topic()` when formatting topic contents.
   - When handling `/cities_all` or `/countries_all`, use `guidebook.get_topic_contents("cities")` / `guidebook.get_topic_contents("countries")` instead of `guidebook.get_info()`.
   - Fetch topic descriptions via `guidebook.get_topic_description(topic)` when needed (currently not used, but available for future enhancements).

5. **Update `TelegramBotAdapter` (`src/adapters/telegram_adapter.py`)**
   - This step is superseded by the "Removing TelegramBotAdapter's Guidebook Dependency" section below.
   - The adapter will use `service.list_topics()` and `service.get_topic_description(topic)` instead of accessing the guidebook directly.

6. **Revise tests**
   - `tests/unit/test_yaml_guidebook.py`:
     - Add tests for `get_topic_description(topic)` with valid and invalid topic names.
     - Add tests for `get_topic_contents(topic)` returning both list and dict structures.
     - Keep coverage for `get_cities(name)` and `get_countries(name)` including vocabulary alias support for subtopic lookups.
     - Remove tests for deprecated methods: `get_info`, `get_results`, `get_descriptions`, `format_results`.
   - `tests/unit/test_berlin_help_service.py`:
     - Update mocks to use new guidebook interface (`get_topic_contents`, `get_topic_description`).
     - Mock the formatter module methods.
     - Ensure the service still renders separators and preserves hashtag prefixes (e.g., `#accommodation\n...`).
   - `tests/unit/test_telegram_adapter.py`:
     - Remove `mock_guidebook` fixture.
     - Mock `service.list_topics()` and `service.get_topic_description(topic)` instead.
     - Update stats recording tests to verify topic descriptions are fetched from service.
   - `tests/unit/test_guidebook_formatter.py` (new file):
     - Test `format_contents()` with list-based contents (simple items).
     - Test `format_contents()` with dict-based contents (keys as section headers or subtopics).
     - Test `format_contents()` with optional title parameter.
     - Test `wrap_with_separator()` produces correct separator format.

7. **Run CI locally**
   - Execute `uv run pytest` after the refactor to confirm behavior parity.

## Removing `TelegramBotAdapter`'s Guidebook Dependency

The adapter currently imports `IGuidebook` to (a) enumerate topics for handler registration (line 74), (b) build `BotCommand`s with human-readable topic descriptions (line 222), and (c) look up topic descriptions while recording statistics (line 250). All of that information already flows through `BerlinHelpService` via its injected guidebook, so we can keep the adapter unaware of guidebook details by expanding the service contract:

1. **Extend `IBerlinHelpService`**
   - Add `list_topics() -> List[str]` to return all topic names. Delegates to `guidebook.get_topics()`.
   - Add `get_topic_description(topic: str) -> Optional[str]` to return a topic description. Delegates to `guidebook.get_topic_description(topic)`.
   - Optionally introduce a `TopicMeta` dataclass (name + topic description) if returning paired metadata is more convenient for command registration.

2. **Update `BerlinHelpService`**
   - Implement the new metadata methods by calling `guidebook.get_topics()` and `guidebook.get_topic_description(topic)`.
   - Consider caching the topic names and topic descriptions to avoid re-reading from YAML on every adapter call, especially when `_bot_commands()` iterates over topics more than once.

3. **Refactor `TelegramBotAdapter`**
   - Drop the `guidebook: IGuidebook` constructor parameter (line 34).
   - Use `service.list_topics()` for handler registration (line 74).
   - Use `service.get_topic_description(topic)` when building `BotCommand` objects in `_bot_commands()` (line 222) and when recording statistics in `_record_stats()` (line 250).
   - Ensure `_record_stats` continues to send a topic description string to `IStatisticsService` by fetching it from the service.

4. **Adjust Composition & Tests**
   - Remove the `guidebook` argument when constructing `TelegramBotAdapter` in `main.py` (lines 27-32); only the service retains the guidebook dependency.
   - Update unit tests in `tests/unit/test_telegram_adapter.py`:
     - Remove the `mock_guidebook` fixture (lines 32-45).
     - Mock `service.list_topics()` and `service.get_topic_description(topic)` instead.
     - Verify that stats recording calls fetch topic descriptions from the service.
     - Note: Auth-related test code has already been removed in commit 494095c.

With this change the adapter talks exclusively to `IBerlinHelpService`, keeping the I/O layer ignorant of the domain data source while the service remains the single consumer of `IGuidebook`.

## Notes on Recent Changes

The authorization and reminder functionality referenced in earlier versions of this document has been removed in commit 494095c (Jan 29, 2026). The current adapter constructor signature is:

```python
def __init__(
    self,
    token: str,
    service: IBerlinHelpService,
    guidebook: IGuidebook,
    stats_service: IStatisticsService,
):
```

This refactoring plan is designed to remove the `guidebook: IGuidebook` parameter, leaving only `service` and `stats_service` as dependencies.
