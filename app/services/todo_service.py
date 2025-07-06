"""
TODO service layer for business logic.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from math import ceil

from app.models.todo import Todo, TodoStatus, TodoPriority
from app.schemas.todo import TodoCreate, TodoUpdate


class TodoService:
    """Service class for TODO operations."""
    
    def __init__(self):
        self._todos: Dict[int, Todo] = {}
        self._next_id = 1
    
    def create_todo(self, todo_data: TodoCreate) -> Todo:
        """Create a new TODO item."""
        todo = Todo(
            id=self._next_id,
            title=todo_data.title,
            description=todo_data.description,
            status=todo_data.status,
            priority=todo_data.priority,
            due_date=todo_data.due_date
        )
        
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo
    
    def get_todo(self, todo_id: int) -> Optional[Todo]:
        """Get a TODO by ID."""
        return self._todos.get(todo_id)
    
    def get_todos(
        self,
        status: Optional[TodoStatus] = None,
        priority: Optional[TodoPriority] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[List[Todo], int]:
        """Get TODOs with optional filtering and pagination."""
        todos = list(self._todos.values())
        
        # Apply filters
        if status:
            todos = [todo for todo in todos if todo.status == status]
        if priority:
            todos = [todo for todo in todos if todo.priority == priority]
        
        # Sort by creation date (newest first)
        todos.sort(key=lambda x: x.created_at, reverse=True)
        
        total = len(todos)
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_todos = todos[start_idx:end_idx]
        
        return paginated_todos, total
    
    def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> Optional[Todo]:
        """Update a TODO item."""
        todo = self._todos.get(todo_id)
        if not todo:
            return None
        
        # Convert Pydantic model to dict, excluding None values
        update_data = todo_data.model_dump(exclude_unset=True, exclude_none=True)
        todo.update(**update_data)
        
        return todo
    
    def delete_todo(self, todo_id: int) -> bool:
        """Delete a TODO item."""
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get TODO statistics."""
        todos = list(self._todos.values())
        total = len(todos)
        
        if total == 0:
            return {
                "total": 0,
                "by_status": {},
                "by_priority": {},
                "overdue": 0
            }
        
        # Count by status
        status_counts = {}
        for status in TodoStatus:
            status_counts[status.value] = len([t for t in todos if t.status == status])
        
        # Count by priority
        priority_counts = {}
        for priority in TodoPriority:
            priority_counts[priority.value] = len([t for t in todos if t.priority == priority])
        
        # Count overdue items
        now = datetime.utcnow()
        overdue = len([t for t in todos if t.due_date and t.due_date < now and t.status != TodoStatus.COMPLETED])
        
        return {
            "total": total,
            "by_status": status_counts,
            "by_priority": priority_counts,
            "overdue": overdue
        }
    
    def clear_all(self):
        """Clear all TODOs (useful for testing)."""
        self._todos.clear()
        self._next_id = 1


# Global service instance
todo_service = TodoService()
