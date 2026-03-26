"""Tests for task API routes (mocked persistence)."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

from models import Task


def _make_task(**kwargs) -> Task:
    defaults: dict = {
        "id": 1,
        "title": "Example",
        "description": "",
        "status": "todo",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    return Task(**defaults)


def test_get_root_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["service"] == "Task Manager API"
    assert data["tasks"] == "/tasks"


def test_get_tasks_returns_200_and_list(client, mock_repo: MagicMock):
    mock_repo.list_all.return_value = [
        _make_task(id=1, title="A"),
        _make_task(id=2, title="B", status="done"),
    ]
    res = client.get("/tasks")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2
    assert data[0]["title"] == "A"
    assert data[0]["description"] == ""
    mock_repo.list_all.assert_called_once()


def test_get_tasks_empty_list_returns_200(client, mock_repo: MagicMock):
    mock_repo.list_all.return_value = []
    res = client.get("/tasks")
    assert res.status_code == 200
    assert res.get_json() == []
    mock_repo.list_all.assert_called_once()


def test_post_tasks_missing_title_returns_400(client, mock_repo: MagicMock):
    res = client.post("/tasks", json={})
    assert res.status_code == 400
    assert res.get_json()["error"] == "title_required"
    mock_repo.create.assert_not_called()


def test_post_tasks_empty_title_returns_400(client, mock_repo: MagicMock):
    res = client.post("/tasks", json={"title": "   "})
    assert res.status_code == 400
    mock_repo.create.assert_not_called()


def test_post_tasks_with_description_creates_and_returns_201(
    client, mock_repo: MagicMock, mock_logger: MagicMock
):
    created = _make_task(
        id=8,
        title="With desc",
        description="Do the thing",
        status="todo",
    )
    mock_repo.create.return_value = created

    res = client.post(
        "/tasks",
        json={"title": "With desc", "description": "Do the thing"},
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["description"] == "Do the thing"
    mock_repo.create.assert_called_once_with("With desc", "Do the thing", "todo")


def test_post_tasks_invalid_description_type_returns_400(client, mock_repo: MagicMock):
    res = client.post("/tasks", json={"title": "Ok", "description": 123})
    assert res.status_code == 400
    assert res.get_json()["error"] == "invalid_description"
    mock_repo.create.assert_not_called()


def test_post_tasks_creates_and_returns_201(
    client, mock_repo: MagicMock, mock_logger: MagicMock
):
    created = _make_task(id=7, title="New task", status="todo")
    mock_repo.create.return_value = created

    res = client.post("/tasks", json={"title": "New task"})
    assert res.status_code == 201
    body = res.get_json()
    assert body["id"] == 7
    assert body["title"] == "New task"
    assert body["description"] == ""
    mock_repo.create.assert_called_once_with("New task", "", "todo")
    mock_logger.log.assert_called_once()
    assert mock_logger.log.call_args[0][0] == "create"


def test_patch_task_not_found_returns_404(client, mock_repo: MagicMock):
    mock_repo.update_status.return_value = None
    res = client.patch("/tasks/99", json={"status": "done"})
    assert res.status_code == 404
    mock_repo.update_status.assert_called_once_with(99, "done")


def test_patch_task_updates_returns_200(
    client, mock_repo: MagicMock, mock_logger: MagicMock
):
    updated = _make_task(id=3, title="X", status="done")
    mock_repo.update_status.return_value = updated

    res = client.patch("/tasks/3", json={"status": "done"})
    assert res.status_code == 200
    assert res.get_json()["status"] == "done"
    mock_logger.log.assert_called_once()
    assert mock_logger.log.call_args[0][0] == "update"


def test_patch_task_missing_status_returns_400(client, mock_repo: MagicMock):
    res = client.patch("/tasks/1", json={})
    assert res.status_code == 400
    mock_repo.update_status.assert_not_called()


def test_delete_task_not_found_returns_404(client, mock_repo: MagicMock):
    mock_repo.delete.return_value = False
    res = client.delete("/tasks/42")
    assert res.status_code == 404
    mock_repo.delete.assert_called_once_with(42)


def test_delete_task_success_returns_200(
    client, mock_repo: MagicMock, mock_logger: MagicMock
):
    mock_repo.delete.return_value = True
    res = client.delete("/tasks/42")
    assert res.status_code == 200
    assert res.get_json()["ok"] is True
    mock_logger.log.assert_called_once()
    assert mock_logger.log.call_args[0][0] == "delete"
