# Kubernetes (Minikube) — backend only

Deploys the **Flask API** image (`backend/Dockerfile`) with **2 replicas** and a **NodePort** service.

Postgres and MongoDB are **not** in these manifests: run them on your machine (e.g. Docker Compose) with **ports published** — see root [`docker-compose.yml`](../docker-compose.yml) (`5432`, `27017`). The ConfigMap uses **`host.minikube.internal`** so pods inside Minikube can reach those services on your host.

## Prerequisites

- **kubectl** and **Minikube** installed.
- Docker (for `docker build` and Compose).

## 0. Start Minikube (required before `kubectl apply`)

The cluster API must be running or `kubectl` will fail with **connection refused** to `127.0.0.1:…` when it tries to validate manifests.

```bash
minikube start
kubectl cluster-info
```

You should see the control plane URL responding (not “connection refused”). If your kubeconfig is stale after a reboot, `minikube start` refreshes it.

## 1. Start databases on the host

From the repo root:

```bash
docker compose up -d postgres mongo
```

Wait until both are healthy (`docker compose ps`).

## 2. Build the image inside Minikube’s Docker

So Kubernetes uses the image without pushing to a registry:

```bash
eval "$(minikube docker-env)"
docker build -t task-manager-backend:latest ./backend
eval "$(minikube docker-env -u)"
```

## 3. Apply manifests

```bash
kubectl apply -f k8s/configmap.yaml -f k8s/deployment.yaml -f k8s/service.yaml
```

## 4. Confirm two pods are running

```bash
kubectl get pods -l app=task-manager-backend
```

Expect **2/2 Running**.

## 5. Open the API URL

**Service URL (NodePort 30080):**

```bash
minikube ip
# then in browser: http://<minikube-ip>:30080/tasks
```

Or:

```bash
minikube service task-manager-backend --url
```

(If that maps port 80 inside the cluster, the printed URL should work; otherwise use `http://$(minikube ip):30080/tasks`.)

## 6. Linux / `host.minikube.internal`

If pods cannot reach the DBs, edit `k8s/configmap.yaml` (or patch the ConfigMap) and replace `host.minikube.internal` with your host gateway IP, or enable Minikube’s host addon:

```bash
minikube ssh "grep host.minikube.internal /etc/hosts"
```

Adjust `DATABASE_URL` / `MONGODB_URI` to match your setup, then:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl rollout restart deployment/task-manager-backend
```
