from datetime import datetime
from app.models import Task, Commit, Status
from app.storage import Storage

VALID_STATUSES = [s.value for s in Status]


class TaskManager:
    def __init__(self, storage: Storage = None):
        self.storage      = storage or Storage()
        self.tasks        = self.storage.load()
        self.active_id: int | None = self._load_active()

    # ── Internal ────────────────────────────────────────────────────────────

    def _save(self):
        self.storage.save(self.tasks)

    def _next_id(self) -> int:
        return max((t.id for t in self.tasks), default=0) + 1

    def _find(self, task_id: int) -> Task:
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            raise ValueError(f"No task with ID #{task_id}.")
        return task

    def _load_active(self) -> int | None:
        """Return the ID of the last non-complete task touched."""
        in_prog = [t for t in self.tasks if t.status == Status.IN_PROGRESS.value]
        return in_prog[-1].id if in_prog else (self.tasks[-1].id if self.tasks else None)

    def _set_active(self, task_id: int):
        self.active_id = task_id

    def _require_active(self) -> Task:
        if not self.active_id:
            raise ValueError("No active task. Use 'task add' or 'task checkout <id>' first.")
        return self._find(self.active_id)

    # ── Commands ─────────────────────────────────────────────────────────────

    def add(self, title: str, context: str = "") -> Task:
        task = Task(
            id      = self._next_id(),
            title   = title,
            context = context,
            status  = Status.PENDING.value,
        )
        self.tasks.append(task)
        self._set_active(task.id)
        self._save()
        return task

    def commit(self, message: str, status: str = None) -> tuple[Task, Commit]:
        task = self._require_active()

        if status:
            if status not in VALID_STATUSES:
                raise ValueError(f"Invalid status '{status}'. Choose: {', '.join(VALID_STATUSES)}")
            task.status = status

        c = Commit(message=message, status=task.status)
        task.commits.append(c)
        task.updated_at = datetime.now().isoformat()
        self._save()
        return task, c

    def push(self, status: str) -> Task:
        """Push a status change — like closing out a task state."""
        task = self._require_active()

        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Choose: {', '.join(VALID_STATUSES)}")

        old_status  = task.status
        task.status = status
        task.updated_at = datetime.now().isoformat()

        # auto-commit the push as a log entry
        c = Commit(message=f"[push] Status changed: {old_status} → {status}", status=status)
        task.commits.append(c)
        self._save()
        return task

    def checkout(self, task_id: int) -> Task:
        """Switch active task — like git checkout."""
        task = self._find(task_id)
        self._set_active(task_id)
        return task

    def log(self, task_id: int = None) -> tuple[Task, list[Commit]]:
        """Show commit history for active or specified task."""
        task = self._find(task_id) if task_id else self._require_active()
        return task, task.commits

    def delete(self, task_id: int) -> Task:
        task = self._find(task_id)
        self.tasks.remove(task)
        if self.active_id == task_id:
            self.active_id = self.tasks[-1].id if self.tasks else None
        self._save()
        return task

    def show(self, status: str = None) -> list[Task]:
        if not status:
            return self.tasks
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Choose: {', '.join(VALID_STATUSES)}")
        return [t for t in self.tasks if t.status == status]

    def search(self, keyword: str) -> list[Task]:
        kw = keyword.lower()
        return [
            t for t in self.tasks
            if kw in t.title.lower() or kw in t.context.lower()
        ]

    def status(self) -> Task:
        """Show active task — like git status."""
        return self._require_active()