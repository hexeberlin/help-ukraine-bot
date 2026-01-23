# Refactoring Opportunities

**Date:** 2026-01-23

This document identifies areas of the codebase that could benefit from refactoring and streamlining.

---

## High Priority Issues

### 1. MongoDB Error Handling (can crash)
- `src/services/articles.py:44-45` - `get()` method doesn't handle `None` result from `find_one()`, will crash with `TypeError`
- `src/services/articles.py:50-55` - `find()` returns raw dicts instead of `Article` objects as type hint claims

### 2. Broken Dataclass Pattern
- `src/models/__init__.py` - `Article` has `@dataclass` decorator but overrides `__init__`, defeating the purpose. Pick one approach.

### 3. Malformed Regex
- `src/services/articles.py:51` - Regex `/.*{text}.*/` has JavaScript-style delimiters that don't work in Python

---

## Medium Priority Issues

### 4. Duplicated Logging Configuration (4 locations)
- `src/commands.py:52-55`
- `src/common.py:13-16`
- `src/services/articles.py:9-12`
- `src/mongo/__init__.py:5-8`

### 5. Duplicated Formatting Functions
- `src/common.py:111-113` - `format_knowledge_results()`
- `src/guidebook.py:83-85` - `_format_results()`

### 6. Type Hint Lies
- `src/services/articles.py:47` - `delete()` claims `-> Article` but returns nothing
- `src/common.py:96` - `parse_article()` typed as `message: str` but receives `Message` object
- `src/common.py:83` - `get_param()` has no type hints at all

### 7. Inefficient Repeated Work
- `src/guidebook.py:110` - Creates lowercase dictionary on every `get_info()` call instead of caching at init
- `src/commands.py:351-353` - Computes `effective_message_type()` twice, ignoring the stored variable

---

## Low Priority Issues

### 8. Unused Code
- `src/commands.py:210-211` - `search_command()` defined but never registered

### 9. Unfinished Validation
- `src/services/articles.py:31-36` - `__validate_keys()` has a TODO for uniqueness check, always returns `True` if non-empty

### 10. Duplicate Delete-Message Logic
- Error handling for `delete_message()` appears in both `src/commands.py:222-225` and `src/common.py:35-38` with inconsistent logging

### 11. Outdated Dependency
- `requirements.txt` - `python-telegram-bot==12.7` is very old (current is 21.x)

---

## Quick Wins

| Issue | Location | Fix |
|-------|----------|-----|
| Use existing variable | `commands.py:351-353` | Use `msg_type` instead of calling `effective_message_type()` again |
| Simplify parse_keys | `common.py:90-93` | `return [k.strip() for k in line.split() if k.strip()]` |
| Fix regex | `articles.py:51` | Remove leading/trailing `/` from pattern |
| Add None check | `articles.py:45` | `if document: return Article(**document)` |
