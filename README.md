# Task Manager (capstone)

Backend API for managing tasks: **Flask**, **PostgreSQL** for task data, **MongoDB** for an append-only activity log.

## Backend layout

| Path | Role |
|------|------|
| `backend/app.py` | Flask app factory; verifies DB connectivity on startup |
| `backend/config.py` | Loads `DATABASE_URL`, `MONGODB_URI`, etc. from environment |
| `backend/models.py` | `Task`, `TaskRepository` (Postgres), `ActivityLogger` (MongoDB) |
| `backend/routes.py` | REST routes under `/tasks` |
| `backend/requirements.txt` | Runtime + test dependencies (pip) |
| `backend/requirements-dev.txt` | Ruff, pre-commit (dev) |
| `backend/ruff.toml` | Ruff lint/format config |
| `backend/tests/` | Pytest suite (repository mocked) |

More detail: **[backend/README.md](backend/README.md)** (lint, pre-commit, CI notes).

## Setup

1. **Python 3.12+** recommended. Create a venv and install deps:

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```

2. **Environment** — copy the example file and edit values for your Postgres and MongoDB:

   ```bash
   cp .env.example .env
   ```

   Required variables:

   - `DATABASE_URL` — PostgreSQL connection URI  
   - `MONGODB_URI` — MongoDB connection URI  
   - `MONGODB_DB_NAME` — optional (default `task_manager`)

3. **Run** (from `backend/`):

   ```bash
   flask --app app:create_app run
   ```

   On success you should see `PostgreSQL: connected.` and `MongoDB: connected.` before the server binds.

## API (summary)

| Method | Path | Notes |
|--------|------|--------|
| `GET` | `/tasks` | List tasks |
| `POST` | `/tasks` | JSON body: `title` (required), `status` optional |
| `PATCH` | `/tasks/<id>` | JSON body: `status` |
| `DELETE` | `/tasks/<id>` | |

## Tests

From `backend/`:

```bash
pytest
```

Uses mocked `TaskRepository` and `ActivityLogger`; no live databases required.

## CI

Lint/format (`ruff`) and `pytest` run on push/PR via **`.github/workflows/ci.yml`** (commands execute in `backend/`).

---

*Frontend, containers, and Kubernetes manifests are not documented here yet.*
