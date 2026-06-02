from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

class Status(str, Enum):
    PENDING     = "pending"
    IN_PROGRESS = "in-progress"
    ON_HOLD     = "on-hold"
    REVIEW      = "review"
    COMPLETE    = "complete"
    DROPPED     = "dropped"


@dataclass
class Commit:
    message:    str
    status:     str
    timestamp:  datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "message":   self.message,
            "status":    self.status,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Commit":
        try:
            timestamp = datetime.fromisoformat(data["timestamp"])
        except (TypeError, ValueError):
            timestamp = datetime.now() # Fallback for corrupted data
        return cls(
            message=data["message"],
            status=data["status"],
            timestamp=timestamp
        )


@dataclass
class Task:
    id:          int
    title:       str
    context:     str          = ""           # -c flag  (what/why)
    status:      Status        = Status.PENDING
    commits:     List[Commit] = field(default_factory=list)
    created_at:  datetime = field(default_factory=datetime.now)
    updated_at:  datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "title":      self.title,
            "context":    self.context,
            "status":     self.status.value,
            "commits":    [c.to_dict() for c in self.commits],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        try:
            created_at = datetime.fromisoformat(data["created_at"])
        except (TypeError, ValueError):
            created_at = datetime.now()

        try:
            updated_at = datetime.fromisoformat(data["updated_at"])
        except (TypeError, ValueError):
            updated_at = datetime.now()

        try:
            status_val = Status(data["status"])
        except ValueError:
            # Fallback to pending if status is invalid
            status_val = Status.PENDING
        commits = [Commit.from_dict(c) for c in data.get("commits", [])]
        return cls(
            id=data["id"],
            title=data["title"],
            context=data.get("context", ""),
            status=status_val,
            commits=commits,
            created_at=created_at,
            updated_at=updated_at,
        )

    @property
    def last_commit(self) -> Optional[Commit]:
        return self.commits[-1] if self.commits else None