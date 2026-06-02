from abc import ABC, abstractmethod
from typing import List, Optional
from app.models import Task

class TaskRepository(ABC):
    """
    Abstract base class defining the contract for task data persistence.
    """
    @abstractmethod
    def load_all(self) -> List[Task]:
        """Loads all tasks from the persistence layer."""
        pass

    @abstractmethod
    def save_all(self, tasks: List[Task]) -> None:
        """Saves the entire list of tasks to the persistence layer."""
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Retrieves a single task by its ID."""
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> List[Task]:
        """Retrieves tasks matching a specific status."""
        pass

    @abstractmethod
    def search_by_keyword(self, keyword: str) -> List[Task]:
        """Retrieves tasks matching a keyword in title or context."""
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Deletes a task by ID. Returns True if successful."""
        pass