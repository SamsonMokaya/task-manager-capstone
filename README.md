# Task Manager (capstone)

Flask API with **PostgreSQL** (tasks) and **MongoDB** (activity logs). Frontend and container docs will live in their own folders when added.

## Repository layout

| Path | README |
|------|--------|
| **[backend/](backend/README.md)** | Python API: venv, pip, env vars, run, tests, Ruff |
| `frontend/` | *(Vue — add when scaffolded)* |
| `k8s/`, `helm/` | *(add when documented)* |

Each top-level area should document its own setup; this file only covers **repo-wide** tooling below.

## Pre-commit

Config: [`.pre-commit-config.yaml`](.pre-commit-config.yaml) at the **repo root** (where `pre-commit install` applies). Hooks currently target **`backend/**/*.py`** (Ruff + whitespace); you can add more file types later.

```bash
pip install -r backend/requirements-dev.txt
pre-commit install
```

```bash
pre-commit run --all-files
```

## CI

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on push/PR: install deps and **Ruff + pytest** with `working-directory: backend`. No local `pre-commit install` required for CI.
