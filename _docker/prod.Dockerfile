FROM python:3.12.8-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
COPY pyproject.toml /app/pyproject.toml
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction

COPY src/server /app/src/server
COPY src/core /app/src/core
COPY config.yml /app/config.yml
COPY _env/prod.env /app/.env


EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "server.app:app", "--workers", "1", "--host", "0.0.0.0", "--port", "8000", "--env-file", ".env"]
