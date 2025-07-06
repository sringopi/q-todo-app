"""
TODO model definitions.
"""
from datetime import datetime
from enum import Enum
from typing import Optional


class TodoStatus(str, Enum):
    """TODO status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TodoPriority(str, Enum):
    """TODO priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo:
    """TODO item model."""
    
    def __init__(
        self,
        id: int,
        title: str,
        description: Optional[str] = None,
        status: TodoStatus = TodoStatus.PENDING,
        priority: TodoPriority = TodoPriority.MEDIUM,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        due_date: Optional[datetime] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.due_date = due_date
    
    def to_dict(self) -> dict:
        """Convert TODO to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }
    
    def update(self, **kwargs):
        """Update TODO fields."""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
