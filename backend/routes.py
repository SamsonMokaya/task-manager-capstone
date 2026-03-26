"""REST API routes for tasks."""

from __future__ import annotations

from enum import StrEnum

from flask import Blueprint, current_app, jsonify, request

from models import ActivityLogger, TaskRepository, TaskStatus


# Copilot review: use an enum for activity log action strings so values stay consistent with MongoDB and typos are caught at edit time.
class ActivityAction(StrEnum):
    """Activity log action types (must match stored strings)."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


def _repo() -> TaskRepository:
    """Return the task repository from the current app config."""
    return current_app.config["TASK_REPOSITORY"]


def _activity_logger() -> ActivityLogger:
    """Return the activity logger from the current app config."""
    return current_app.config["ACTIVITY_LOGGER"]


# Copilot review: return stable error codes plus a human message so API clients can branch on `error` without parsing free text.
def _validate_status(value: str | None) -> tuple[str | None, tuple[dict, int] | None]:
    """Validate status; return (value, None) or (None, (error_body, status_code))."""
    if value is None:
        return None, (
            {"error": "status_required", "message": "Status is required"},
            400,
        )
    if value not in TaskStatus.values():
        return None, (
            {
                "error": "invalid_status",
                "message": "Invalid status value",
                "allowed": sorted(TaskStatus.values()),
            },
            400,
        )
    return value, None


# Copilot review: pull title checks into a helper so POST stays readable and empty/whitespace titles fail the same way everywhere.
def _validate_title(title: str | None) -> tuple[str | None, tuple[dict, int] | None]:
    """Validate title; return (stripped title, None) or (None, (error_body, status_code))."""
    if not isinstance(title, str) or not title.strip():
        return None, (
            {"error": "title_required", "message": "Title is required"},
            400,
        )
    return title.strip(), None


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.get("/tasks")
def list_tasks():
    """List all tasks."""
    tasks = _repo().list_all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.post("/tasks")
def create_task():
    """Create a new task."""
    # Copilot review: require `application/json` and respond with 415 instead of failing later with a vague 400 when the body is not JSON.
    if not request.is_json:
        return (
            jsonify(
                {
                    "error": "invalid_content_type",
                    "message": "Content-Type must be application/json",
                }
            ),
            415,
        )

    payload = request.get_json() or {}

    title, err = _validate_title(payload.get("title"))
    if err:
        body, code = err
        return jsonify(body), code

    status_raw = payload.get("status", TaskStatus.TODO.value)
    status, err = _validate_status(status_raw)
    if err:
        body, code = err
        return jsonify(body), code

    task = _repo().create(title, status)
    _activity_logger().log(
        ActivityAction.CREATE.value,
        task.id,
        f"Created task #{task.id}: {task.title!r}",
    )
    return jsonify(task.to_dict()), 201


@tasks_bp.patch("/tasks/<int:task_id>")
def update_task_status(task_id: int):
    """Update task status."""
    # Copilot review: same JSON guard as POST so PATCH rejects non-JSON bodies explicitly.
    if not request.is_json:
        return (
            jsonify(
                {
                    "error": "invalid_content_type",
                    "message": "Content-Type must be application/json",
                }
            ),
            415,
        )

    payload = request.get_json() or {}
    status_raw = payload.get("status")
    status, err = _validate_status(status_raw)
    if err:
        body, code = err
        return jsonify(body), code

    task = _repo().update_status(task_id, status)
    if task is None:
        return (
            jsonify(
                {
                    "error": "task_not_found",
                    "message": f"Task {task_id} not found",
                }
            ),
            404,
        )

    _activity_logger().log(
        ActivityAction.UPDATE.value,
        task.id,
        f"Updated status for task #{task.id} to {task.status!r}",
    )
    return jsonify(task.to_dict()), 200


@tasks_bp.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    """Delete a task."""
    deleted = _repo().delete(task_id)
    if not deleted:
        return (
            jsonify(
                {
                    "error": "task_not_found",
                    "message": f"Task {task_id} not found",
                }
            ),
            404,
        )

    _activity_logger().log(
        ActivityAction.DELETE.value,
        task_id,
        f"Deleted task #{task_id}",
    )
    return jsonify({"ok": True}), 200
