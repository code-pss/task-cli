from app.repository import TaskRepository
from app.models import Task, Commit, Status
from datetime import datetime
from typing import List, Optional

# The Status Enum is used to define available statuses.
VALID_STATUSES = [s.value for s in Status]

# The TaskManager now depends on the TaskRepository interface, not the concrete Storage implementation.
class TaskManager:
    def __init__(self, repository: TaskRepository):
        self.repository = repository
        self.tasks = self.repository.load_all()
        self.active_id: Optional[int] = self._load_active()

    # ── Internal ────────────────────────────────────────────────────────────

    def _save(self):
        self.repository.save_all(self.tasks)

    def _next_id(self) -> int:
        return max((t.id for t in self.tasks), default=0) + 1

    def _find(self, task_id: int) -> Task:
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            raise ValueError(f"No task with ID #{task_id}.")
        return task

    def _load_active(self) -> Optional[int]:
        """Return the ID of the last non-complete task touched."""
        in_prog = [t for t in self.tasks if t.status == Status.IN_PROGRESS]
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
            status  = Status.PENDING,
        )
        self.tasks.append(task)
        self._set_active(task.id)
        self._save()
        return task

    def commit(self, message: str, status: Optional[str] = None) -> tuple[Task, Commit]:
        task = self._require_active()

        # Handle status change validation
        if status:
            try:
                new_status = Status(status)
                task.status = new_status
            except ValueError:
                raise ValueError(f"Invalid status '{status}'. Choose from available statuses.")

        c = Commit(message=message, status=task.status)
        task.commits.append(c)
        task.updated_at = datetime.now() # Updated to use datetime object
        self._save()
        return task, c

    def push(self, status: str) -> Task:
        """Push a status change — like closing out a task state."""
        task = self._require_active()

        try:
            new_status = Status(status)
        except ValueError:
            raise ValueError(f"Invalid status '{status}'. Choose from available statuses.")

        old_status  = task.status
        task.status = new_status
        task.updated_at = datetime.now()

        # auto-commit the push as a log entry
        c = Commit(message=f"[push] Status changed: {old_status.value} → {new_status.value}", status=new_status)
        task.commits.append(c)
        self._save()
        return task

    def checkout(self, task_id: int) -> Task:
        """Switch active task — like git checkout."""
        task = self._find(task_id)
        self._set_active(task_id)
        return task

    def log(self, task_id: Optional[int] = None) -> tuple[Task, List[Commit]]:
        """Show commit history for active or specified task."""
        task = self._find(task_id) if task_id else self._require_active()
        return task, task.commits

    def delete(self, task_id: int) -> Task:
        task = self._find(task_id)

        # Use the repository delete method
        success = self.repository.delete(task_id)
        if not success:
            raise ValueError(f"Task with ID {task_id} not found.")

        self.tasks.remove(task) # Remove from in-memory cache
        if self.active_id == task_id:
            self.active_id = self.repository.load_all()[-1].id if self.repository.load_all() else None
        self._save()
        return task

    def show(self, status: Optional[str] = None) -> list[Task]:
        if status:
            try:
                status_enum = Status(status)
                return self.repository.find_by_status(status_enum.value)
            except ValueError:
                raise ValueError(f"Invalid status '{status}'. Choose from available statuses.")
        return self.tasks
    def search(self, keyword: str) -> list[Task]:
        return self.repository.search_by_keyword(keyword)
    def status(self) -> Task:
        """Show active task — like git status."""
        return self._require_active()