from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


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
    timestamp:  str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "message":   self.message,
            "status":    self.status,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Commit":
        return cls(**data)


@dataclass
class Task:
    id:          int
    title:       str
    context:     str          = ""           # -c flag  (what/why)
    status:      str          = Status.PENDING.value
    commits:     list         = field(default_factory=list)
    created_at:  str          = field(default_factory=lambda: datetime.now().isoformat())
    updated_at:  str          = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "title":      self.title,
            "context":    self.context,
            "status":     self.status,
            "commits":    [c.to_dict() if isinstance(c, Commit) else c for c in self.commits],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        data["commits"] = [Commit.from_dict(c) for c in data.get("commits", [])]
        return cls(**data)

    @property
    def last_commit(self) -> Commit | None:
        return self.commits[-1] if self.commits else None