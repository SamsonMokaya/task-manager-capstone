"""Configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Application configuration."""

    database_url: str
    mongodb_uri: str | None  # None only when tests inject a mock logger
    mongodb_db_name: str = "task_manager"

    @classmethod
    def from_env(cls) -> Config:
        """Load settings from ``DATABASE_URL``, ``MONGODB_URI``, and optional ``MONGODB_DB_NAME``."""
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise RuntimeError(
                "DATABASE_URL is required (PostgreSQL connection string)."
            )
        mongodb_uri = os.environ.get("MONGODB_URI")
        if not mongodb_uri:
            raise RuntimeError(
                "MONGODB_URI is required (MongoDB connection string)."
            )
        mongodb_db_name = os.environ.get("MONGODB_DB_NAME", "task_manager")
        return cls(
            database_url=database_url,
            mongodb_uri=mongodb_uri,
            mongodb_db_name=mongodb_db_name,
        )
