# Task Manager (capstone project)

## Overview

This is a **task board** API and UI: create, list, update status, and delete tasks. **PostgreSQL** stores task rows; **MongoDB** stores an **activity log** of changes. It is aimed at **developers learning** a small full-stack setup with containers and optional **Kubernetes (Minikube)** for the API.

## Tech stack

| Layer | Technologies |
|--------|----------------|
| Frontend | **Vue 3**, **Vite**, **TypeScript** |
| Backend | **Python 3**, **Flask**, **Gunicorn**, **Spectree** (OpenAPI) |
| Data | **PostgreSQL** (tasks), **MongoDB** (activity log) |
| Containers | **Docker**, **Docker Compose** |
| Kubernetes | **Minikube**, **kubectl**; optional **Helm** chart under [`helm/task-manager/`](helm/task-manager/) |
| Quality | **Ruff**, **pytest**, **pre-commit**, **GitHub Actions** CI |

## Architecture

```
[ Browser ]
     |
     v
[ Vue 3 (Vite dev server :5173) ]  --HTTP/JSON-->  [ Flask API ]
                                                      |         |
                                                      |         +--> [ MongoDB ]  (activity logs)
                                                      |
                                                      +--> [ PostgreSQL ]  (tasks)

Optional (path B): Flask runs inside Minikube as Pods; Vue still on host.
Compose runs Postgres + Mongo on the host; API pods reach them via host.minikube.internal.
```

## Quick start — full stack with Docker Compose

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) (Compose v2 included).

1. Clone the repo and open the **repository root** (`task-manager-capstone/`).

2. Start **PostgreSQL**, **MongoDB**, and the **backend** API:

   ```bash
   docker compose up --build
   ```

   Wait until containers are healthy. The API is at **http://localhost:5001** on the host (e.g. `GET http://localhost:5001/tasks`). The container listens on **5000**; Compose maps **5001→5000** so macOS can keep using **5000** (often **Control Center / AirPlay**). To expose **5000** on the host instead, free port 5000 (see `lsof -i :5000`) and set `ports: ["5000:5000"]` in [`docker-compose.yml`](docker-compose.yml).

3. In another terminal, start the **frontend** (from repo root):

   ```bash
   cd frontend
   cp .env.example .env.development
   ```

   Ensure **`VITE_API_BASE_URL=http://127.0.0.1:5001`** in `.env.development`, then:

   ```bash
   npm install
   npm run dev
   ```

4. Open the URL Vite prints (usually **http://localhost:5173**). The UI loads tasks from the API; ensure **CORS** defaults match (see [backend/README.md](backend/README.md)).

No local Python venv is required for this path—only Docker and Node.

## How to run (alternative paths)

Both paths below need **PostgreSQL** and **MongoDB** reachable with the credentials in **`k8s/configmap.yaml`** or **`backend/.env`**. Databases are **not** deployed inside Minikube in this repo; they run on your machine (usually via Docker Compose).

| Path | What you start | Best for |
|------|----------------|----------|
| **A — All in Docker Compose** | From repo root: `docker compose up` | Simplest: API at **http://localhost:5001** (host), DBs in containers, no Kubernetes. |
| **B — Backend in Kubernetes (Minikube)** | **1.** `docker compose up -d postgres mongo` (DBs only). **2.** Build image in Minikube’s Docker and apply manifests as in **[k8s/README.md](k8s/README.md)** (or install the **[Helm](helm/task-manager/)** chart instead of raw YAML—use one method for Deployment + Service). | API runs as pods; DBs stay on the host (`5432`, `27017`). |

**Order for path B:** `minikube start` → `docker compose up -d postgres mongo` → build image + apply manifests → `minikube service task-manager-backend --url`. Point **`VITE_API_BASE_URL`** at the URL Minikube prints (or NodePort **30080**).

## API reference (summary)

Base URL depends on how you run the backend (e.g. `http://127.0.0.1:5001` under Compose). **`Content-Type: application/json`** is required for bodies below.

| Method | Path | Request body | Success response |
|--------|------|----------------|------------------|
| `GET` | `/` | — | **200** JSON: `service`, `tasks`, `docs` links |
| `GET` | `/tasks` | — | **200** JSON array of task objects (`id`, `title`, `description`, `status`, …) |
| `POST` | `/tasks` | `{ "title": string, "description"?: string, "status"?: string }` | **201** created task object; **400** validation errors; **415** if not JSON |
| `PATCH` | `/tasks/<id>` | `{ "status": string }` | **200** updated task; **400** / **404** / **415** as applicable |
| `DELETE` | `/tasks/<id>` | — | **200** `{ "ok": true }`; **404** if missing |

Interactive docs: **Spectree** at `/apidoc/swagger` when the server is running (see [backend/README.md](backend/README.md) for the base URL).

## Repository layout

| Path | README |
|------|--------|
| **[backend/](backend/README.md)** | Python API: venv, env vars, Flask, Docker Compose, tests, Ruff |
| **[frontend/](frontend/README.md)** | Vue 3 + Vite task UI |
| [`docker-compose.yml`](docker-compose.yml) | Postgres + Mongo + backend services |
| **[k8s/](k8s/README.md)** | ConfigMap + Deployment + Service (Minikube) |
| **[helm/task-manager/](helm/task-manager/)** | Helm chart (same workload as `k8s/` templates) |

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
