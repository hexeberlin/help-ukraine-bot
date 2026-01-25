# Refactoring Opportunities

**Date:** 2026-01-23

**Note:** MongoDB and Articles service were removed on 2026-01-25. Several issues listed below were resolved by that removal (issues #1, #2, #3, #9, and parts of #4 and #6).

This document identifies areas of the codebase that could benefit from refactoring and streamlining.

---

## High Priority Issues

### 1. ~~MongoDB Error Handling~~ ✅ RESOLVED
- Removed with MongoDB/Articles service removal (2026-01-25)

### 2. ~~Broken Dataclass Pattern~~ ✅ RESOLVED
- Removed with MongoDB/Articles service removal (2026-01-25)

### 3. ~~Malformed Regex~~ ✅ RESOLVED
- Removed with MongoDB/Articles service removal (2026-01-25)

---

## Medium Priority Issues

### 4. Duplicated Logging Configuration (2 locations)
- `src/commands.py:52-55`
- `src/common.py:13-16`

### 5. Duplicated Formatting Functions
- `src/common.py:111-113` - `format_knowledge_results()`
- `src/guidebook.py:83-85` - `_format_results()`

### 6. Type Hint Lies
- `src/common.py:83` - `get_param()` has no type hints at all

### 7. Inefficient Repeated Work
- `src/guidebook.py:110` - Creates lowercase dictionary on every `get_info()` call instead of caching at init
- `src/commands.py:351-353` - Computes `effective_message_type()` twice, ignoring the stored variable

---

## Low Priority Issues

### 8. Unused Code
- `src/commands.py:210-211` - `search_command()` defined but never registered

### 9. ~~Unfinished Validation~~ ✅ RESOLVED
- Removed with MongoDB/Articles service removal (2026-01-25)

### 10. Duplicate Delete-Message Logic
- Error handling for `delete_message()` appears in both `src/commands.py:222-225` and `src/common.py:35-38` with inconsistent logging

### 11. Outdated Dependency
- `requirements.txt` - `python-telegram-bot==12.7` is very old (current is 21.x)

---

## Quick Wins

| Issue | Location | Fix |
|-------|----------|-----|
| Use existing variable | `commands.py:~290` | Use `msg_type` instead of calling `effective_message_type()` again |
