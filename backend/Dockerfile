# Flask API — use with docker-compose at the repo root.
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# create_app() runs after Postgres + Mongo are healthy (see compose healthchecks).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
