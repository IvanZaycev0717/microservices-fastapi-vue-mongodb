#!/bin/bash

echo "🎯 Running Python isort..."
cd src
poetry run isort .
cd ..

echo "🎯 Running Python ruff formatting (line length 79)..."
cd src  
poetry run ruff format --line-length 79 .
cd ..

echo "🎯 Running Python ruff linter (remove unused imports)..."
cd src
poetry run ruff check --select F401 --fix .
cd ..

echo "🎯 Running JavaScript/TypeScript formatting..."
cd admin_gui
npm run format
cd ..

echo "🎯 Running JavaScript/TypeScript linting..."
cd admin_gui
npm run lint
cd ..

echo "✅ All formatting complete!"