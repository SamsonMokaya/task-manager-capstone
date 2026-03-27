# Task UI (Vue 3 + Vite)

Task list UI in **`TaskBoard.vue`**: load tasks, add (title + description), change status, delete, and filter client-side.

## API URL (environment variables)

1. Copy the template once (same folder as `package.json`):

   ```bash
   cp .env.example .env.development
   ```

2. Edit **`.env.development`** and set **`VITE_API_BASE_URL`** to your Flask base URL **with no trailing slash**:

   - **Docker Compose backend:** `http://127.0.0.1:5001` (host port; container listens on 5000)
   - **Local `flask run`:** `http://127.0.0.1:5000`
   - **Minikube backend:** use the URL from `minikube service task-manager-backend --url` (no trailing slash), or `http://<minikube-ip>:30080` — see [k8s/README.md](../k8s/README.md)

**`.env.development`** is **not** committed (each developer keeps their own). Only **[`.env.example`](.env.example)** is in git. For secrets or overrides, use **`.env.local`** or **`.env.*.local`** (gitignored).

The backend must allow browser requests from the Vite dev origin (`http://localhost:5173` by default); see **CORS** in [backend/README.md](../backend/README.md).

## Commands

```bash
npm install
npm run dev
npm run lint
npm run build
```
