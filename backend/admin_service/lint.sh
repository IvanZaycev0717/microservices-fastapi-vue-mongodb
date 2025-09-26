#!/bin/bash

echo "🎯 Running isort..."
isort .

echo "🎯 Running ruff formatting (line length 79)..."
ruff format --line-length 79 .

echo "🎯 Running ruff linter (remove unused imports)..."
ruff check --select F401 --fix .

echo "✅ Formatting complete!"