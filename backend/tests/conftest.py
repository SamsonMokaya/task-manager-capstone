"""Pytest fixtures."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app import create_app
from config import Config


@pytest.fixture
def mock_repo() -> MagicMock:
    """Stand-in ``TaskRepository`` (no real PostgreSQL)."""
    return MagicMock()


@pytest.fixture
def mock_logger() -> MagicMock:
    """Stand-in ``ActivityLogger`` (no real MongoDB)."""
    return MagicMock()


@pytest.fixture
def app(mock_repo: MagicMock, mock_logger: MagicMock):
    """Flask app with mocked persistence."""
    cfg = Config(
        database_url="postgresql://test:test@localhost/test",
        mongodb_uri="mongodb://127.0.0.1:27017/",
    )
    application = create_app(
        config=cfg,
        task_repository=mock_repo,
        activity_logger=mock_logger,
    )
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    """HTTP client for route tests."""
    return app.test_client()
