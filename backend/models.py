"""Domain models, PostgreSQL task persistence, and MongoDB activity logging."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import psycopg2
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Allowed task status values."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

    @classmethod
    def values(cls) -> frozenset[str]:
        """All allowed status string values."""
        return frozenset(s.value for s in cls)


def _utc_now() -> datetime:
    """Current time in UTC (timezone-aware)."""
    return datetime.now(UTC)


@dataclass
class Task:
    """Task entity."""

    id: int
    title: str
    status: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON responses (ISO timestamps)."""
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


def _row_to_task(row: tuple[Any, ...]) -> Task:
    """Map a ``tasks`` table row to a ``Task`` instance."""
    return Task(
        id=row[0],
        title=row[1],
        status=row[2],
        created_at=row[3],
        updated_at=row[4],
    )


class TaskRepository:
    """PostgreSQL persistence for tasks."""

    def __init__(self, database_url: str) -> None:
        """``database_url``: libpq connection string (e.g. from ``DATABASE_URL``)."""
        self._dsn = database_url

    def _connect(self) -> psycopg2.extensions.connection:
        """Open a new connection (caller should use as context manager or close)."""
        return psycopg2.connect(self._dsn)

    def verify_connection(self) -> None:
        """Confirm PostgreSQL accepts connections."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")

    def ensure_schema(self) -> None:
        """Create the tasks table if it does not exist."""
        ddl = """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            status VARCHAR(64) NOT NULL DEFAULT 'todo',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
            conn.commit()

    def list_all(self) -> list[Task]:
        """Return all tasks ordered by id."""
        sql = """
        SELECT id, title, status, created_at, updated_at
        FROM tasks
        ORDER BY id ASC
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [_row_to_task(row) for row in rows]

    def create(self, title: str, status: str = TaskStatus.TODO.value) -> Task:
        """Insert a task and return the persisted row (including id and timestamps)."""
        sql = """
        INSERT INTO tasks (title, status)
        VALUES (%s, %s)
        RETURNING id, title, status, created_at, updated_at
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (title, status))
                row = cur.fetchone()
            conn.commit()
        assert row is not None
        return _row_to_task(row)

    def update_status(self, task_id: int, status: str) -> Task | None:
        """Update status by id; return the task or ``None`` if id does not exist."""
        sql = """
        UPDATE tasks
        SET status = %s, updated_at = NOW()
        WHERE id = %s
        RETURNING id, title, status, created_at, updated_at
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (status, task_id))
                row = cur.fetchone()
            conn.commit()
        if row is None:
            return None
        return _row_to_task(row)

    def delete(self, task_id: int) -> bool:
        """Delete by id; return whether a row was removed."""
        sql = "DELETE FROM tasks WHERE id = %s"
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (task_id,))
                deleted = cur.rowcount > 0
            conn.commit()
        return deleted


def verify_mongodb_connection(uri: str, timeout_ms: int = 3000) -> None:
    """Verify MongoDB is reachable (``admin`` ping); raise on failure."""
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=timeout_ms,
        connectTimeoutMS=timeout_ms,
    )
    try:
        client.admin.command("ping")
    finally:
        client.close()


class ActivityLogger:
    """Append-only activity log in MongoDB (collection: activity_logs)."""

    COLLECTION_NAME = "activity_logs"
    _MONGO_TIMEOUT_MS = 3000

    def __init__(self, mongodb_uri: str, db_name: str = "task_manager") -> None:
        """``db_name`` selects the database; logs go to collection ``activity_logs``."""
        self._uri = mongodb_uri
        self._db_name = db_name
        self._client: MongoClient | None = None
        self._collection: Collection | None = None
        self._mongodb_unavailable = False

    def _get_collection(self) -> Collection | None:
        """Lazily open client and return ``activity_logs`` collection, or ``None`` if disabled."""
        if not self._uri or self._mongodb_unavailable:
            return None
        if self._collection is None:
            self._client = MongoClient(
                self._uri,
                serverSelectionTimeoutMS=self._MONGO_TIMEOUT_MS,
                connectTimeoutMS=self._MONGO_TIMEOUT_MS,
            )
            self._collection = self._client[self._db_name][self.COLLECTION_NAME]
        return self._collection

    def log(
        self,
        action: str,
        task_id: int | None,
        description: str,
    ) -> None:
        """Record a create, update, or delete event. Never raises; failures are logged."""
        if self._mongodb_unavailable:
            logger.debug("Activity log skipped (MongoDB unavailable): %s", description)
            return
        coll = self._get_collection()
        if coll is None:
            logger.debug("Activity log skipped (no collection): %s", description)
            return
        doc = {
            "timestamp": _utc_now(),
            "action": action,
            "task_id": task_id,
            "description": description,
        }
        try:
            coll.insert_one(doc)
        except PyMongoError as exc:
            logger.warning(
                "MongoDB activity log failed (%s); further logs skipped until restart: %s",
                action,
                exc,
            )
            self._mongodb_unavailable = True
            self.close()

    def close(self) -> None:
        """Close the Mongo client if open."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._collection = None
