"""Flask application factory."""

from __future__ import annotations

import os

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from models import ActivityLogger, TaskRepository, verify_mongodb_connection
from openapi import spec
from routes import tasks_bp


def create_app(
    config: Config | None = None,
    *,
    task_repository: TaskRepository | None = None,
    activity_logger: ActivityLogger | None = None,
) -> Flask:
    """
    Create and configure the Flask app.

    When using real repositories (default), verifies PostgreSQL and MongoDB before
    registering routes. For tests, pass ``task_repository`` and ``activity_logger``
    mocks; optional ``config`` avoids loading credentials from the environment.
    """
    app = Flask(__name__)

    # Browser clients (Vite dev server, etc.): comma-separated origins in CORS_ORIGINS
    _cors_origins = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    CORS(
        app,
        resources={r"/*": {"origins": [o.strip() for o in _cors_origins if o.strip()]}},
    )

    if config is None:
        config = Config.from_env()

    repo = task_repository or TaskRepository(config.database_url)

    if task_repository is None:
        try:
            repo.verify_connection()
            repo.ensure_schema()
        except Exception as exc:
            raise RuntimeError(
                "Cannot connect to PostgreSQL. Check DATABASE_URL and that the server is running."
            ) from exc
        print("PostgreSQL: connected.", flush=True)

    if activity_logger is None:
        if not config.mongodb_uri:
            raise RuntimeError("MONGODB_URI is required.")
        try:
            verify_mongodb_connection(config.mongodb_uri)
        except Exception as exc:
            raise RuntimeError(
                "Cannot connect to MongoDB. Check MONGODB_URI and that the server is running."
            ) from exc
        print("MongoDB: connected.", flush=True)
        logger = ActivityLogger(
            config.mongodb_uri,
            config.mongodb_db_name,
        )
    else:
        logger = activity_logger

    app.config["TASK_REPOSITORY"] = repo
    app.config["ACTIVITY_LOGGER"] = logger

    app.register_blueprint(tasks_bp)
    spec.register(app)

    @app.get("/")
    def root():
        """Landing JSON for `GET /` (browser or curl to the server root)."""
        return jsonify(
            {
                "service": "Task Manager API",
                "tasks": "/tasks",
                "docs": "/apidoc/swagger",
            }
        )

    return app


# Local dev: `cd backend && flask --app app:create_app run`
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    create_app().run(host="0.0.0.0", port=port, debug=True)
