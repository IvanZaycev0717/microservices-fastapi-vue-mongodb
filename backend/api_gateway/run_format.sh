#!/bin/bash


echo "🎯 Running Python ruff formatting (line length 79)..."
cd src  
poetry run ruff format --line-length 79 .
cd ..

echo "🎯 Running Python ruff linter (remove unused imports)..."
cd src
poetry run ruff check --select F401 --fix .
cd ..

echo "✅ All formatting complete!"