#!/bin/bash
# Generate requirements.txt from pyproject.toml for Heroku deployment

set -e

echo "Generating requirements.txt from uv.lock..."

# Generate requirements.txt with a warning header
{
    echo "# ==================================================================================="
    echo "# WARNING: This file is AUTO-GENERATED from pyproject.toml via uv"
    echo "# DO NOT EDIT MANUALLY - Your changes will be overwritten"
    echo "# To update dependencies: modify pyproject.toml, run 'uv lock', then regenerate this"
    echo "# Regenerate with: ./scripts/generate_requirements.sh"
    echo "# ==================================================================================="
    echo ""
    uv export --frozen --no-hashes --no-dev --no-editable | grep -v "^\.$"
} > requirements.txt

echo "requirements.txt generated successfully"
