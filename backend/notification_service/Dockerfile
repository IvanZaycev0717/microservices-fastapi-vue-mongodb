FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

CMD ["poetry", "run", "python", "src/main.py"]