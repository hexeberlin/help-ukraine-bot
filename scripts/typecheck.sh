#!/usr/bin/env bash
set -euo pipefail

uv run mypy src --no-incremental
