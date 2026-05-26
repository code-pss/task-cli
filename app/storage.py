import json
from pathlib import Path
from app.models import Task

DATA_FILE = Path("data/tasks.json")


class Storage:
    def __init__(self, filepath: Path = DATA_FILE):
        self.filepath = filepath
        self.filepath.parent.mkdir(exist_ok=True)

    def load(self) -> list[Task]:
        if not self.filepath.exists():
            return []
        with open(self.filepath, "r") as f:
            raw = json.load(f)
            return [Task.from_dict(t) for t in raw]

    def save(self, tasks: list[Task]) -> None:
        with open(self.filepath, "w") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)