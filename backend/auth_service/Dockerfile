FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY src/ ./src/
COPY scripts/ ./scripts/

RUN poetry run python scripts/generate_proto.py

EXPOSE 50052

CMD ["poetry", "run", "python", "src/main.py"]