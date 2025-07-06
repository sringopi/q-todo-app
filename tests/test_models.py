"""
Tests for TODO models and business logic.
"""
import pytest
from datetime import datetime, timedelta

from app.models.todo import Todo, TodoStatus, TodoPriority


class TestTodoModel:
    """Test TODO model functionality."""
    
    def test_todo_creation_with_defaults(self):
        """Test TODO creation with default values."""
        todo = Todo(id=1, title="Test TODO")
        
        assert todo.id == 1
        assert todo.title == "Test TODO"
        assert todo.description is None
        assert todo.status == TodoStatus.PENDING
        assert todo.priority == TodoPriority.MEDIUM
        assert isinstance(todo.created_at, datetime)
        assert isinstance(todo.updated_at, datetime)
        assert todo.due_date is None
    
    def test_todo_creation_with_all_fields(self):
        """Test TODO creation with all fields specified."""
        created_at = datetime.utcnow()
        updated_at = datetime.utcnow()
        due_date = datetime.utcnow() + timedelta(days=7)
        
        todo = Todo(
            id=1,
            title="Complete TODO",
            description="A complete TODO item",
            status=TodoStatus.IN_PROGRESS,
            priority=TodoPriority.HIGH,
            created_at=created_at,
            updated_at=updated_at,
            due_date=due_date
        )
        
        assert todo.id == 1
        assert todo.title == "Complete TODO"
        assert todo.description == "A complete TODO item"
        assert todo.status == TodoStatus.IN_PROGRESS
        assert todo.priority == TodoPriority.HIGH
        assert todo.created_at == created_at
        assert todo.updated_at == updated_at
        assert todo.due_date == due_date
    
    def test_todo_to_dict(self):
        """Test TODO conversion to dictionary."""
        todo = Todo(
            id=1,
            title="Test TODO",
            description="Test description",
            status=TodoStatus.COMPLETED,
            priority=TodoPriority.LOW
        )
        
        todo_dict = todo.to_dict()
        
        assert todo_dict["id"] == 1
        assert todo_dict["title"] == "Test TODO"
        assert todo_dict["description"] == "Test description"
        assert todo_dict["status"] == "completed"
        assert todo_dict["priority"] == "low"
        assert "created_at" in todo_dict
        assert "updated_at" in todo_dict
        assert todo_dict["due_date"] is None
    
    def test_todo_update(self):
        """Test TODO update functionality."""
        todo = Todo(id=1, title="Original Title")
        original_updated_at = todo.updated_at
        
        # Small delay to ensure updated_at changes
        import time
        time.sleep(0.001)
        
        todo.update(
            title="Updated Title",
            description="New description",
            status=TodoStatus.COMPLETED
        )
        
        assert todo.title == "Updated Title"
        assert todo.description == "New description"
        assert todo.status == TodoStatus.COMPLETED
        assert todo.updated_at > original_updated_at
    
    def test_todo_update_with_none_values(self):
        """Test TODO update ignores None values."""
        todo = Todo(
            id=1,
            title="Original Title",
            description="Original description"
        )
        
        todo.update(
            title="Updated Title",
            description=None,  # Should be ignored
            status=TodoStatus.COMPLETED
        )
        
        assert todo.title == "Updated Title"
        assert todo.description == "Original description"  # Unchanged
        assert todo.status == TodoStatus.COMPLETED
    
    def test_todo_update_invalid_attribute(self):
        """Test TODO update with invalid attribute."""
        todo = Todo(id=1, title="Test TODO")
        
        # This should not raise an error, just ignore invalid attributes
        todo.update(invalid_field="invalid_value")
        
        assert not hasattr(todo, "invalid_field")


class TestTodoEnums:
    """Test TODO enumeration classes."""
    
    def test_todo_status_values(self):
        """Test TodoStatus enum values."""
        assert TodoStatus.PENDING.value == "pending"
        assert TodoStatus.IN_PROGRESS.value == "in_progress"
        assert TodoStatus.COMPLETED.value == "completed"
    
    def test_todo_priority_values(self):
        """Test TodoPriority enum values."""
        assert TodoPriority.LOW.value == "low"
        assert TodoPriority.MEDIUM.value == "medium"
        assert TodoPriority.HIGH.value == "high"
    
    def test_enum_comparison(self):
        """Test enum comparison functionality."""
        assert TodoStatus.PENDING == TodoStatus.PENDING
        assert TodoStatus.PENDING != TodoStatus.COMPLETED
        
        assert TodoPriority.HIGH == TodoPriority.HIGH
        assert TodoPriority.LOW != TodoPriority.HIGH
