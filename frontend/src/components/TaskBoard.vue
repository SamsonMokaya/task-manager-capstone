<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const filter = ref('all')

const tasks = ref([])
const loading = ref(false)
const error = ref(null)

const modalOpen = ref(false)
/** Task shown in read-only “View” modal (full title / description). */
const viewingTask = ref(null)

const newTitle = ref('')
const newDescription = ref('')
const titleError = ref(null)
const formError = ref(null)

const apiBase = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5001'
).replace(/\/$/, '')

const STATUS_OPTIONS = [
  { value: 'todo', label: 'Todo' },
  { value: 'in_progress', label: 'In progress' },
  { value: 'done', label: 'Done' },
]

const filteredTasks = computed(() => {
  if (filter.value === 'all') {
    return tasks.value
  }
  return tasks.value.filter((t) => t.status === filter.value)
})

function statusLabel(status) {
  const found = STATUS_OPTIONS.find((o) => o.value === status)
  return found ? found.label : status
}

function openViewModal(task) {
  viewingTask.value = task
}

function closeViewModal() {
  viewingTask.value = null
}

function openAddModal() {
  newTitle.value = ''
  newDescription.value = ''
  titleError.value = null
  formError.value = null
  modalOpen.value = true
}

function closeAddModal() {
  modalOpen.value = false
}

function onDocumentKeydown(e) {
  if (e.key !== 'Escape') return
  if (viewingTask.value) {
    closeViewModal()
  } else if (modalOpen.value) {
    closeAddModal()
  }
}

async function fetchTasks() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`${apiBase}/tasks`)
    if (!res.ok) {
      throw new Error(`Could not load tasks (${res.status})`)
    }
    tasks.value = await res.json()
  } catch (e) {
    error.value =
      e instanceof Error ? e.message : 'Failed to load tasks. Is the API running?'
  } finally {
    loading.value = false
  }
}

async function addTask() {
  const title = newTitle.value.trim()
  if (!title) {
    titleError.value = 'Title is required.'
    formError.value = null
    return
  }
  titleError.value = null
  formError.value = null
  loading.value = true
  try {
    const res = await fetch(`${apiBase}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        description: newDescription.value.trim(),
      }),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.message || `Create failed (${res.status})`)
    }
    newTitle.value = ''
    newDescription.value = ''
    closeAddModal()
    await fetchTasks()
  } catch (e) {
    formError.value = e instanceof Error ? e.message : 'Could not create task'
  } finally {
    loading.value = false
  }
}

function clearTitleError() {
  titleError.value = null
}

async function updateStatus(id, status) {
  error.value = null
  loading.value = true
  try {
    const res = await fetch(`${apiBase}/tasks/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.message || `Update failed (${res.status})`)
    }
    await fetchTasks()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not update task'
  } finally {
    loading.value = false
  }
}

async function removeTask(id) {
  error.value = null
  loading.value = true
  try {
    const res = await fetch(`${apiBase}/tasks/${id}`, { method: 'DELETE' })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.message || `Delete failed (${res.status})`)
    }
    await fetchTasks()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not delete task'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTasks()
  window.addEventListener('keydown', onDocumentKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onDocumentKeydown)
})
</script>

<template>
  <div class="board">
    <header class="toolbar">
      <div class="toolbar__left">
        <h1 class="toolbar__title">Tasks</h1>
        <p class="toolbar__hint">API: {{ apiBase }}</p>
      </div>
      <button type="button" class="btn btn--primary" @click="openAddModal">Add task</button>
    </header>

    <div class="toolbar toolbar--filters">
      <span class="filters-label">Show</span>
      <div class="filters" role="group" aria-label="Filter by status">
        <button
          type="button"
          class="filter"
          :class="{ 'filter--active': filter === 'all' }"
          @click="filter = 'all'"
        >
          All
        </button>
        <button
          type="button"
          class="filter"
          :class="{ 'filter--active': filter === 'todo' }"
          @click="filter = 'todo'"
        >
          Todo
        </button>
        <button
          type="button"
          class="filter"
          :class="{ 'filter--active': filter === 'in_progress' }"
          @click="filter = 'in_progress'"
        >
          In progress
        </button>
        <button
          type="button"
          class="filter"
          :class="{ 'filter--active': filter === 'done' }"
          @click="filter = 'done'"
        >
          Done
        </button>
      </div>
    </div>

    <p v-if="error" class="banner banner--error" role="alert">{{ error }}</p>
    <p v-if="loading && tasks.length === 0" class="banner">Loading…</p>

    <div v-else class="table-wrap" aria-live="polite">
      <table v-if="filteredTasks.length" class="task-table">
        <thead>
          <tr>
            <th scope="col">Title</th>
            <th scope="col">Description</th>
            <th scope="col">Status</th>
            <th scope="col" class="task-table__col-actions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in filteredTasks" :key="task.id">
            <td class="task-table__title">
              <span class="task-table__cell-clip" :title="task.title">{{ task.title }}</span>
            </td>
            <td class="task-table__desc">
              <span
                v-if="task.description"
                class="task-table__cell-clip"
                :title="task.description"
              >{{ task.description }}</span>
              <span v-else class="task-table__muted">—</span>
            </td>
            <td class="task-table__status">
              <label class="sr-only" :for="`status-${task.id}`">Status</label>
              <select
                :id="`status-${task.id}`"
                class="task-table__select"
                :value="task.status"
                @change="updateStatus(task.id, $event.target.value)"
              >
                <option v-for="opt in STATUS_OPTIONS" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </td>
            <td class="task-table__actions">
              <div class="task-table__action-btns">
                <button
                  type="button"
                  class="btn btn--sm btn--outline"
                  @click="openViewModal(task)"
                >
                  View
                </button>
                <button
                  type="button"
                  class="btn btn--sm btn--danger"
                  @click="removeTask(task.id)"
                >
                  Remove
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else-if="!loading && tasks.length === 0" class="empty">No tasks yet. Use “Add task” to create one.</p>
      <p v-else-if="!loading && tasks.length > 0" class="empty">No tasks match this filter.</p>
    </div>

    <Teleport to="body">
      <div
        v-if="modalOpen"
        class="modal-backdrop"
        @click.self="closeAddModal"
      >
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          class="modal"
          tabindex="-1"
          @click.stop
        >
          <div class="modal__head">
            <h2 id="modal-title" class="modal__title">New task</h2>
            <button type="button" class="modal__close" aria-label="Close" @click="closeAddModal">
              ×
            </button>
          </div>
          <form class="modal__form" @submit.prevent="addTask">
            <label class="field">
              <span class="field__label">Title</span>
              <input
                v-model="newTitle"
                class="field__input"
                :class="{ 'field__input--invalid': titleError }"
                type="text"
                name="title"
                autocomplete="off"
                placeholder="What needs doing?"
                :aria-invalid="titleError ? 'true' : 'false'"
                :aria-describedby="titleError ? 'title-error' : undefined"
                @input="clearTitleError"
              />
              <p v-if="titleError" id="title-error" class="field__error" role="alert">
                {{ titleError }}
              </p>
            </label>
            <label class="field">
              <span class="field__label">Description</span>
              <textarea
                v-model="newDescription"
                class="field__input field__input--multiline"
                name="description"
                rows="3"
                placeholder="Optional details"
              />
            </label>
            <p v-if="formError" class="form__error" role="alert">{{ formError }}</p>
            <div class="modal__actions">
              <button type="button" class="btn btn--ghost" @click="closeAddModal">Cancel</button>
              <button class="btn btn--primary" type="submit" :disabled="loading">Add</button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <Teleport to="body">
      <div
        v-if="viewingTask"
        class="modal-backdrop"
        @click.self="closeViewModal"
      >
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="view-modal-title"
          class="modal modal--wide"
          tabindex="-1"
          @click.stop
        >
          <div class="modal__head">
            <h2 id="view-modal-title" class="modal__title">Task details</h2>
            <button type="button" class="modal__close" aria-label="Close" @click="closeViewModal">
              ×
            </button>
          </div>
          <div class="modal__body modal__body--detail">
            <dl class="detail-list">
              <dt>Title</dt>
              <dd>{{ viewingTask.title }}</dd>
              <dt>Description</dt>
              <dd>
                <span v-if="viewingTask.description" class="detail-list__pre">{{
                  viewingTask.description
                }}</span>
                <span v-else class="detail-list__empty">No description</span>
              </dd>
              <dt>Status</dt>
              <dd>{{ statusLabel(viewingTask.status) }}</dd>
              <template v-if="viewingTask.created_at">
                <dt>Created</dt>
                <dd>{{ viewingTask.created_at }}</dd>
              </template>
              <template v-if="viewingTask.updated_at">
                <dt>Updated</dt>
                <dd>{{ viewingTask.updated_at }}</dd>
              </template>
            </dl>
            <div class="modal__actions modal__actions--single">
              <button type="button" class="btn btn--primary" @click="closeViewModal">Close</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.board {
  max-width: 56rem;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 2.5rem;
  min-height: 100%;
  color: #0f172a;
  background: #fff;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.toolbar--filters {
  align-items: center;
  padding-bottom: 1rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.toolbar__left {
  min-width: 0;
}

.toolbar__title {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #0f172a;
}

.toolbar__hint {
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: #475569;
}

.filters-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
  margin-right: 0.5rem;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}

.filter {
  padding: 0.4rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  background: #fff;
  font: inherit;
  font-size: 0.875rem;
  color: #0f172a;
  cursor: pointer;
}

.filter--active {
  border-color: #2563eb;
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 600;
}

.banner {
  margin: 0.75rem 0 1rem;
  font-size: 0.9rem;
  color: #475569;
}

.banner--error {
  color: #b91c1c;
}

.table-wrap {
  margin-top: 0.5rem;
  overflow-x: auto;
}

.task-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9375rem;
}

.task-table th {
  text-align: left;
  padding: 0.65rem 0.75rem;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #334155;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.task-table td {
  padding: 0.65rem 0.75rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.task-table tbody tr:hover {
  background: #fafafa;
}

.task-table__title {
  font-weight: 600;
  color: #0f172a;
  max-width: 12rem;
  overflow: hidden;
}

.task-table__desc {
  color: #334155;
  max-width: min(22rem, 40vw);
  overflow: hidden;
}

.task-table__cell-clip {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-table__muted {
  color: #94a3b8;
}

.task-table__status {
  white-space: nowrap;
}

.task-table__select {
  padding: 0.35rem 0.5rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
  font: inherit;
  font-size: 0.875rem;
  color: #0f172a;
  background: #fff;
  min-width: 9rem;
}

.task-table__actions {
  text-align: right;
  white-space: nowrap;
}

.task-table__action-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: flex-end;
  align-items: center;
}

.task-table__col-actions {
  width: 11rem;
  text-align: right;
}

.empty {
  padding: 2rem 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.95rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  font: inherit;
  font-size: 0.9375rem;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn--primary {
  background: #2563eb;
  color: #fff;
}

.btn--primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn--sm {
  padding: 0.35rem 0.65rem;
  font-size: 0.8125rem;
  border-radius: 0.375rem;
}

.btn--danger {
  background: #fef2f2;
  color: #b91c1c;
  border-color: #fecaca;
}

.btn--danger:hover:not(:disabled) {
  background: #fee2e2;
  border-color: #fca5a5;
}

.btn--outline {
  background: #fff;
  color: #2563eb;
  border-color: #93c5fd;
}

.btn--outline:hover:not(:disabled) {
  background: #eff6ff;
  border-color: #60a5fa;
}

.btn--ghost {
  background: #fff;
  color: #334155;
  border-color: #cbd5e1;
}

.btn--ghost:hover:not(:disabled) {
  background: #f8fafc;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.45);
}

.modal {
  width: 100%;
  max-width: 26rem;
  max-height: 90vh;
  overflow-y: auto;
  background: #fff;
  border-radius: 0.75rem;
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(0, 0, 0, 0.05);
  color: #0f172a;
}

.modal--wide {
  max-width: 32rem;
}

.modal__body {
  padding: 1.25rem;
}

.modal__body--detail {
  padding-top: 0;
}

.modal__actions--single {
  justify-content: flex-end;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.detail-list {
  margin: 0;
}

.detail-list dt {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #64748b;
  margin: 1rem 0 0.35rem;
}

.detail-list dt:first-child {
  margin-top: 0;
}

.detail-list dd {
  margin: 0 0 0.25rem;
  font-size: 0.9375rem;
  color: #0f172a;
  line-height: 1.5;
}

.detail-list__pre {
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-list__empty {
  color: #94a3b8;
  font-style: italic;
}

.modal__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal__title {
  font-size: 1.125rem;
  font-weight: 700;
}

.modal__close {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 0.375rem;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  color: #64748b;
  cursor: pointer;
}

.modal__close:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.modal__form {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field__label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
}

.field__input {
  padding: 0.5rem 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  font: inherit;
  color: #0f172a;
  background-color: #fff;
}

.field__input--invalid {
  border-color: #dc2626;
}

.field__error {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: #b91c1c;
}

.form__error {
  margin: 0;
  font-size: 0.9rem;
  color: #b91c1c;
}

.field__input--multiline {
  resize: vertical;
  min-height: 4rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
