"""WSGI entry for production servers (e.g. Gunicorn in Docker)."""

from app import create_app

app = create_app()
