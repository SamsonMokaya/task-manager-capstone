"""OpenAPI / Spectree: request-response models for documentation only."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, RootModel
from spectree import SpecTree

spec = SpecTree(
    "flask",
    title="Task Manager API",
    version="1.0.0",
    # No leading slash: path="/apidoc" would make spec_url "//apidoc/openapi.json",
    # which browsers resolve as a different host (protocol-relative URL), breaking ReDoc.
    path="apidoc",
    # Docs-only: we use skip_validation on routes and read Flask's request ourselves.
    # annotations=True (Spectree default) conflicts with skip_validation and spams warnings.
    annotations=False,
)


class TaskResponse(BaseModel):
    """Single task returned by the API."""

    model_config = ConfigDict(extra="forbid")

    id: int
    title: str
    status: str
    created_at: str = Field(..., description="ISO 8601 timestamp")
    updated_at: str = Field(..., description="ISO 8601 timestamp")


class TaskListResponse(RootModel[list[TaskResponse]]):
    """GET /tasks response body."""


class CreateTaskBody(BaseModel):
    """POST /tasks JSON body."""

    title: str = Field(..., min_length=1, description="Task title")
    status: str | None = Field(
        None,
        description="One of: todo, in_progress, done (default: todo)",
    )


class PatchTaskBody(BaseModel):
    """PATCH /tasks/<id> JSON body."""

    status: str = Field(..., description="New status: todo, in_progress, or done")


class ErrorBody(BaseModel):
    """Typical error JSON (shape varies slightly by endpoint)."""

    model_config = ConfigDict(extra="allow")

    error: str
    message: str | None = None
    allowed: list[str] | None = None


class DeleteOkResponse(BaseModel):
    """DELETE success body."""

    ok: bool = True
