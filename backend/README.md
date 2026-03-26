# Backend (Flask API)

**pip** only: `requirements.txt` and `requirements-dev.txt` (no Poetry). Ruff config: **`ruff.toml`** in this directory.

Copy-paste commands (run, curl CRUD, docs, pytest): **[COMMANDS.md](COMMANDS.md)**.

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

Edit `.env`:

- `DATABASE_URL` — PostgreSQL URI (required)
- `MONGODB_URI` — MongoDB URI (required for app startup)
- `MONGODB_DB_NAME` — optional (default `task_manager`)

## Run

```bash
flask --app app:create_app run
```

On success you should see `PostgreSQL: connected.` and `MongoDB: connected.` before the server listens.

## API (summary)

| Method | Path | Notes |
|--------|------|--------|
| `GET` | `/tasks` | List tasks |
| `POST` | `/tasks` | JSON: `title` (required), `status` optional |
| `PATCH` | `/tasks/<id>` | JSON: `status` |
| `DELETE` | `/tasks/<id>` | |

## API docs (OpenAPI)

With the server running, **Spectree** serves interactive docs (paths are under **`/apidoc`** by default):

- **Swagger UI:** [http://127.0.0.1:5000/apidoc/swagger](http://127.0.0.1:5000/apidoc/swagger)
- **ReDoc:** [http://127.0.0.1:5000/apidoc/redoc](http://127.0.0.1:5000/apidoc/redoc)
- **OpenAPI JSON:** [http://127.0.0.1:5000/apidoc/openapi.json](http://127.0.0.1:5000/apidoc/openapi.json)

Schemas live in **`openapi.py`**; route handlers use `skip_validation=True` so your existing validation and status codes stay unchanged—docs are for exploration only.

## Lint & format

```bash
ruff check .
ruff format .
```

## Tests

```bash
pytest
```

Mocks `TaskRepository` and `ActivityLogger` — no live databases needed.

## Pre-commit & CI

- **Pre-commit** is configured at the [repo root](../README.md#pre-commit); run `pre-commit install` from there after `pip install -r backend/requirements-dev.txt`.
- **CI**: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs Ruff and pytest in this directory on push/PR.
