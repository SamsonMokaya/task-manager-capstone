# Task Manager (capstone project)

Flask API with **PostgreSQL** (tasks) and **MongoDB** (activity logs). A **Vue 3** frontend lives in [`frontend/`](frontend/README.md).

## How to run (pick one path)

Both paths need **PostgreSQL** and **MongoDB** reachable with the same credentials your env/ConfigMap use. The databases are **not** inside Minikube in this repo; they run on your machine (usually via Docker Compose).

| Path | What you start | Best for |
|------|----------------|----------|
| **A — All in Docker Compose** | From repo root: `docker compose up` | Simplest: API at **http://localhost:5001**, DBs in containers, no Kubernetes. |
| **B — Backend in Kubernetes (Minikube)** | **1.** `docker compose up -d postgres mongo` (DBs only). **2.** Build image in Minikube’s Docker and `kubectl apply` as in **[k8s/README.md](k8s/README.md)**. | API runs as pods; DBs stay on the host via published ports (`5432`, `27017`). |

**Order for path B:** start **Minikube** (`minikube start`), then **Compose for `postgres` + `mongo` only**, then **build + apply** the backend manifests. The frontend (`npm run dev`) points `VITE_API_BASE_URL` at whichever API URL you use (Compose `5001`, or the URL from `minikube service … --url`).

## Repository layout

| Path | README |
|------|--------|
| **[backend/](backend/README.md)** | Python API: venv, pip, env vars, run, Docker Compose, tests, Ruff |
| [`docker-compose.yml`](docker-compose.yml) | Postgres + Mongo + backend (see backend README) |
| **[frontend/](frontend/README.md)** | Vue 3 + Vite task UI (`TaskBoard.vue`) |
| **[k8s/](k8s/README.md)** | Backend Deployment (2 replicas) + NodePort (Minikube) |

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

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on push/PR: install deps and **Ruff + pytest** with `working-directory: backend`.
