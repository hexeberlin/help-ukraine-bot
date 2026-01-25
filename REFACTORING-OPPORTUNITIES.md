# Refactoring Opportunities

**Date:** 2026-01-23

**Note:** MongoDB and Articles service were removed on 2026-01-25. Several issues listed below were resolved by that removal (issues #1, #2, #3, #9, and parts of #4 and #6).

This document identifies areas of the codebase that could benefit from refactoring and streamlining.

---

## Open

### 11. Outdated Dependency
- `requirements.txt` - `python-telegram-bot==12.7` is very old (current is 21.x)

---

## Resolved

### High Priority

#### 1. ~~MongoDB Error Handling~~ ✅ RESOLVED
- Removed with MongoDB/Articles service removal (2026-01-25)

#### 2. ~~Broken Dataclass Pattern~~ ✅ RESOLVED
- Removed with MongoDB/Articles service removal (2026-01-25)

#### 3. ~~Malformed Regex~~ ✅ RESOLVED
- Removed with MongoDB/Articles service removal (2026-01-25)

### Medium Priority

#### 4. ~~Duplicated Logging Configuration~~ ✅ RESOLVED
- Removed duplicate from `src/commands.py` (2026-01-25)

#### 5. ~~Duplicated Formatting Functions~~ ✅ RESOLVED
- Consolidated into `Guidebook.format_results()` as public static method (2026-01-25)

#### 6. ~~Type Hint Lies~~ ✅ RESOLVED
- Added type hints to `get_param()` (2026-01-25)

#### 7. ~~Inefficient Repeated Work~~ ✅ RESOLVED
- Cached lowercase dictionary at init in `Guidebook.__init__()` (2026-01-25)
- Fixed duplicate `effective_message_type()` call in `delete_greetings()` (2026-01-25)

### Low Priority

#### 8. ~~Unused Code~~ ✅ RESOLVED
- Removed `search_command()` from commands.py (2026-01-25)

#### 9. ~~Unfinished Validation~~ ✅ RESOLVED
- Removed with MongoDB/Articles service removal (2026-01-25)

#### 10. ~~Duplicate Delete-Message Logic~~ ✅ RESOLVED
- Consolidated to use `delete_command()` from common.py consistently (2026-01-25)

## Quick Wins

All quick wins have been resolved! ✅
