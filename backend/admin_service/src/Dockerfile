FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y poppler-utils postgresql-client && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["poetry", "run", "python", "main.py"]