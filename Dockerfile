FROM python:3.11-buster as builder

RUN pip install poetry==1.5.0

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

FROM python:3.11-slim-buster as runtime


ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . /seeya_server

WORKDIR /seeya_server

EXPOSE 8080

ARG SEEYA_ENV=prod \
    SEEYA_SECRET_KEY \
    SEEYA_DB_NAME \
    SEEYA_DB_USER \
    SEEYA_DB_PASSWORD \
    SEEYA_DB_HOST \
    SEEYA_DB_PORT \
    SEEYA_S3_BUCKET_NAME \
    AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY

ENV SEEYA_ENV=${SEEYA_ENV} \
    SEEYA_SECRET_KEY=${SEEYA_SECRET_KEY} \
    SEEYA_DB_NAME=${SEEYA_DB_NAME} \
    SEEYA_DB_USER=${SEEYA_DB_USER} \
    SEEYA_DB_PASSWORD=${SEEYA_DB_PASSWORD} \
    SEEYA_DB_HOST=${SEEYA_DB_HOST} \
    SEEYA_DB_PORT=${SEEYA_DB_PORT} \
    SEEYA_S3_BUCKET_NAME=${SEEYA_S3_BUCKET_NAME} \
    AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

CMD uvicorn seeya_server.asgi:application --host 0.0.0.0 --port 8080 --log-config log.${SEEYA_ENV}.ini
