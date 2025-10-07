#!/bin/bash

poetry run ruff format src/ --line-length=79
poetry run ruff check src/ --select I --fix
poetry run isort src/ --profile black --float-to-top --remove-redundant-aliases --combine-as

echo "✨ Formatting completed!"