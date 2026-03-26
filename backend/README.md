# Backend (Flask API)

Python dependencies are managed with **pip** and `requirements.txt` / `requirements-dev.txt` (no Poetry).

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # then edit DATABASE_URL and MONGODB_URI
```

## Lint & format (Ruff)

Config: **`ruff.toml`** in this directory.

```bash
cd backend
ruff check .
ruff format .
```

## Tests

```bash
cd backend
pytest
```

## Pre-commit (optional)

From the **repository root** (required by the pre-commit tool):

```bash
pip install -r backend/requirements-dev.txt
pre-commit install
```

Hooks only touch files under `backend/`.

## CI

GitHub Actions only reads workflows from the repo root. The workflow file is **`../.github/workflows/ci.yml`**; it runs the same commands as above with `working-directory: backend`.
