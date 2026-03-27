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

### CORS (browser / Vue dev server)

The API enables **Flask-CORS** for origins in **`CORS_ORIGINS`** (comma-separated). Default: `http://localhost:5173` and `http://127.0.0.1:5173` (Vite). Override if your frontend runs elsewhere, e.g.:

```bash
export CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:3000
```

## Docker Compose

From the **repository root** (not `backend/`):

```bash
docker compose up
```

Use `docker compose up --build` after changing the Dockerfile or dependencies.

This starts **PostgreSQL** (named volume `postgres_data`), **MongoDB** (`mongo_data`), and the **backend** (Gunicorn + `wsgi:app`). The API is on **`http://localhost:5001`** on the host (maps to port 5000 in the container; see `docker-compose.yml`).

## API (summary)

| Method | Path | Notes |
|--------|------|--------|
| `GET` | `/` | Service info and links (JSON) |
| `GET` | `/tasks` | List tasks |
| `POST` | `/tasks` | JSON: `title` (required), `description` optional, `status` optional |
| `PATCH` | `/tasks/<id>` | JSON: `status` |
| `DELETE` | `/tasks/<id>` | |

## API docs (OpenAPI)

With the server running, **Spectree** serves interactive docs (paths are under **`/apidoc`** by default). Use the **same host and port** as your API (e.g. **`http://127.0.0.1:5000`** for local `flask run`, **`http://127.0.0.1:5001`** for Docker Compose):

- **Swagger UI:** `http://127.0.0.1:<port>/apidoc/swagger`
- **ReDoc:** `http://127.0.0.1:<port>/apidoc/redoc`
- **OpenAPI JSON:** `http://127.0.0.1:<port>/apidoc/openapi.json`

Schemas live in **`openapi.py`**; route handlers use `skip_validation=True` so your existing validation and status codes stay unchanged—docs are for exploration only.

## Lint & format

```bash
ruff check .
ruff format .
```

## Tests

Tests are in **`tests/`**. They use **mocked** `TaskRepository` and `ActivityLogger` (`conftest.py`), so they never talk to PostgreSQL or MongoDB. You do **not** need a special env flag or Compose stack running—`create_app` is called with fake config and injected mocks.

### Virtual environment (same as CI)

From **`backend/`** after [Setup](#setup):

```bash
pytest
```

With dev tools (Ruff) installed: `pip install -r requirements-dev.txt`, then `ruff check .` as in [Lint & format](#lint--format).

### Docker

From the **repository root**, run pytest inside the backend image. **`--no-deps`** skips Postgres and Mongo (tests do not need them):

```bash
docker compose run --rm --no-deps backend pytest
```
