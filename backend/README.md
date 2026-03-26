# Backend (Flask API)

**pip** only: `requirements.txt` and `requirements-dev.txt` (no Poetry). Ruff config: **`ruff.toml`** in this directory.

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
