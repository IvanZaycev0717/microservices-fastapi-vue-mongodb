#!/bin/bash

echo "🎨 Formatting code with Ruff..."
poetry run ruff format src/ --line-length=79

echo "📚 Checking and fixing docstrings..."
poetry run ruff check src/ --select D --fix

echo "🔧 Sorting imports..."
poetry run ruff check src/ --select I --fix

echo "✨ Formatting completed!"