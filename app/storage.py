from app.repository import TaskRepository
from app.models import Task
import json
from pathlib import Path
from typing import Optional

DATA_FILE = Path("data/tasks.json")


class Storage(TaskRepository):
    def __init__(self, filepath: Path = DATA_FILE):
        self.filepath = filepath
        self.filepath.parent.mkdir(exist_ok=True)

    def load_all(self) -> list[Task]:
        if not self.filepath.exists():
            return []
        with open(self.filepath, "r") as f:
            raw = json.load(f)
            return [Task.from_dict(t) for t in raw]

    def save_all(self, tasks: list[Task]) -> None:
        with open(self.filepath, "w") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)

    def get_by_id(self, task_id: int) -> Optional[Task]:
        tasks = self.load_all()
        return next((t for t in tasks if t.id == task_id), None)

    def find_by_status(self, status: str) -> list[Task]:
        tasks = self.load_all()
        return [t for t in tasks if t.status == status]

    def search_by_keyword(self, keyword: str) -> list[Task]:
        tasks = self.load_all()
        kw = keyword.lower()
        return [
            t for t in tasks
            if kw in t.title.lower() or kw in t.context.lower()
        ]

    def delete(self, task_id: int) -> bool:
        tasks = self.load_all()
        initial_count = len(tasks)
        new_tasks = [t for t in tasks if t.id != task_id]
        if len(new_tasks) < initial_count:
            self.save_all(new_tasks)
            return True
        return False
