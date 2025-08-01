FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv pip install --no-cache-dir --system .

COPY . .

RUN uv run python manage.py collectstatic --noinput
