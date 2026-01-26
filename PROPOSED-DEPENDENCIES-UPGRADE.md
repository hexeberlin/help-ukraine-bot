# Proposed Dependency Upgrades

The table below captures every pinned dependency from `requirements.txt` along with the latest version currently published on PyPI and the recommended upgrade guidance.

| Dependency | Current | Latest (PyPI) | Recommendation |
| --- | --- | --- | --- |
| `python-telegram-bot[webhooks]` | 21.11 | 22.6 | Jump to the 22.x line to get Bot API 7.10 features and multiple webhook fixes; adjust `tests/test_deps.py` so the guard matches the new baseline before releasing. |
| `requests` | 2.26.0 | 2.32.5 | Either drop the unused dependency or upgrade together with `urllib3`, `certifi`, and `charset-normalizer` because 2.32.x depends on the modern HTTP stack. |
| `urllib3` | 1.26.8 | 2.6.3 | Required when upgrading `requests`; note the 2.x branch removed some legacy TLS shims, so run the test suite (especially webhook code) after bumping. |
| `certifi` | 2021.10.8 | 2026.1.4 | Update alongside the HTTP stack to ensure the bundled CA store has the latest trust roots. |
| `charset-normalizer` | 2.0.12 | 3.4.4 | Update with the HTTP stack; there are multiple bug and security fixes plus performance wins for UTF-8 heavy responses. |
| `cryptography` | 36.0.1 | 46.0.3 | Upgrade to pick up OpenSSL 3.x compatibility and CVE fixes; this implies raising `cffi`/`pycparser` per below. |
| `cffi` | 1.15.0 | 2.0.0 | Required by the new `cryptography` wheels; verify the OS build pipeline (if any) still works because 2.0 ships new ABI bindings. |
| `pycparser` | 2.21 | 3.0 | Upgrade to match `cffi`’s upper-bound expectations. |
| `PyYAML` | 6.0 | 6.0.3 | Contains fixes for loader bugs that affect `safe_load` usage in `src/guidebook.py`. |
| `toml` | 0.10.2 | 0.10.2 | Already at the final release; consider migrating to `tomllib` (stdlib) when bumping the minimum Python version so you can drop this dependency later. |
| `pytest` | ~=7.3 | 9.0.2 | Gain asyncio fixture improvements that better model PTB handlers; expect minor rewrites to deprecated plugin hooks. |
| `pylint` | ~=2.17 | 4.0.4 | Upgrade to get Python 3.11 awareness; update `.pylintrc` if new checkers surface. |

## Suggested Upgrade Order

1. Bump `python-telegram-bot` to 22.x and update `tests/test_deps.py` so CI enforces the new minimum version.
2. Modernize the HTTP/TLS stack (`requests`, `urllib3`, `certifi`, `charset-normalizer`) in one PR to keep the dependency graph consistent, then re-run the webhook tests.
3. Upgrade `cryptography`, `cffi`, and `pycparser` together; verify Heroku builds still compile the wheels if a pre-built one is not available.
4. Refresh `PyYAML`; no code changes expected since `safe_load` remains stable.
5. Update developer tooling (`pytest`, `pylint`) and address any warnings or fixture migrations flagged during CI.
