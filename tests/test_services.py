"""
Tests for TODO service layer.
"""
import pytest
from datetime import datetime, timedelta

from app.services.todo_service import TodoService
from app.schemas.todo import TodoCreate, TodoUpdate
from app.models.todo import TodoStatus, TodoPriority


class TestTodoService:
    """Test TODO service functionality."""
    
    @pytest.fixture
    def service(self):
        """Create a fresh TODO service instance."""
        return TodoService()
    
    @pytest.fixture
    def sample_todo_create(self):
        """Sample TodoCreate schema."""
        return TodoCreate(
            title="Test TODO",
            description="Test description",
            status=TodoStatus.PENDING,
            priority=TodoPriority.MEDIUM
        )
    
    def test_create_todo(self, service: TodoService, sample_todo_create: TodoCreate):
        """Test TODO creation."""
        todo = service.create_todo(sample_todo_create)
        
        assert todo.id == 1
        assert todo.title == sample_todo_create.title
        assert todo.description == sample_todo_create.description
        assert todo.status == sample_todo_create.status
        assert todo.priority == sample_todo_create.priority
        assert isinstance(todo.created_at, datetime)
        assert isinstance(todo.updated_at, datetime)
    
    def test_create_multiple_todos(self, service: TodoService):
        """Test creating multiple TODOs with incremental IDs."""
        todo1 = service.create_todo(TodoCreate(title="First TODO"))
        todo2 = service.create_todo(TodoCreate(title="Second TODO"))
        todo3 = service.create_todo(TodoCreate(title="Third TODO"))
        
        assert todo1.id == 1
        assert todo2.id == 2
        assert todo3.id == 3
    
    def test_get_todo_existing(self, service: TodoService, sample_todo_create: TodoCreate):
        """Test retrieving an existing TODO."""
        created_todo = service.create_todo(sample_todo_create)
        retrieved_todo = service.get_todo(created_todo.id)
        
        assert retrieved_todo is not None
        assert retrieved_todo.id == created_todo.id
        assert retrieved_todo.title == created_todo.title
    
    def test_get_todo_non_existing(self, service: TodoService):
        """Test retrieving a non-existing TODO."""
        todo = service.get_todo(999)
        assert todo is None
    
    def test_get_todos_empty(self, service: TodoService):
        """Test getting TODOs when none exist."""
        todos, total = service.get_todos()
        assert todos == []
        assert total == 0
    
    def test_get_todos_with_data(self, service: TodoService):
        """Test getting TODOs with existing data."""
        # Create test TODOs
        service.create_todo(TodoCreate(title="TODO 1", priority=TodoPriority.HIGH))
        service.create_todo(TodoCreate(title="TODO 2", status=TodoStatus.IN_PROGRESS))
        service.create_todo(TodoCreate(title="TODO 3", status=TodoStatus.COMPLETED))
        
        todos, total = service.get_todos()
        
        assert len(todos) == 3
        assert total == 3
        # Should be sorted by creation date (newest first)
        assert todos[0].title == "TODO 3"
        assert todos[1].title == "TODO 2"
        assert todos[2].title == "TODO 1"
    
    def test_get_todos_filter_by_status(self, service: TodoService):
        """Test filtering TODOs by status."""
        service.create_todo(TodoCreate(title="Pending TODO", status=TodoStatus.PENDING))
        service.create_todo(TodoCreate(title="In Progress TODO", status=TodoStatus.IN_PROGRESS))
        service.create_todo(TodoCreate(title="Completed TODO", status=TodoStatus.COMPLETED))
        
        # Filter by pending status
        todos, total = service.get_todos(status=TodoStatus.PENDING)
        assert len(todos) == 1
        assert total == 1
        assert todos[0].status == TodoStatus.PENDING
        
        # Filter by completed status
        todos, total = service.get_todos(status=TodoStatus.COMPLETED)
        assert len(todos) == 1
        assert total == 1
        assert todos[0].status == TodoStatus.COMPLETED
    
    def test_get_todos_filter_by_priority(self, service: TodoService):
        """Test filtering TODOs by priority."""
        service.create_todo(TodoCreate(title="High Priority", priority=TodoPriority.HIGH))
        service.create_todo(TodoCreate(title="Medium Priority", priority=TodoPriority.MEDIUM))
        service.create_todo(TodoCreate(title="Low Priority", priority=TodoPriority.LOW))
        
        # Filter by high priority
        todos, total = service.get_todos(priority=TodoPriority.HIGH)
        assert len(todos) == 1
        assert total == 1
        assert todos[0].priority == TodoPriority.HIGH
    
    def test_get_todos_pagination(self, service: TodoService):
        """Test TODO pagination."""
        # Create 15 TODOs
        for i in range(15):
            service.create_todo(TodoCreate(title=f"TODO {i+1}"))
        
        # Test first page
        todos, total = service.get_todos(page=1, page_size=5)
        assert len(todos) == 5
        assert total == 15
        
        # Test second page
        todos, total = service.get_todos(page=2, page_size=5)
        assert len(todos) == 5
        assert total == 15
        
        # Test last page
        todos, total = service.get_todos(page=3, page_size=5)
        assert len(todos) == 5
        assert total == 15
        
        # Test page beyond available data
        todos, total = service.get_todos(page=4, page_size=5)
        assert len(todos) == 0
        assert total == 15
    
    def test_update_todo_existing(self, service: TodoService, sample_todo_create: TodoCreate):
        """Test updating an existing TODO."""
        created_todo = service.create_todo(sample_todo_create)
        
        update_data = TodoUpdate(
            title="Updated Title",
            status=TodoStatus.COMPLETED
        )
        
        updated_todo = service.update_todo(created_todo.id, update_data)
        
        assert updated_todo is not None
        assert updated_todo.title == "Updated Title"
        assert updated_todo.status == TodoStatus.COMPLETED
        assert updated_todo.description == sample_todo_create.description  # Unchanged
    
    def test_update_todo_non_existing(self, service: TodoService):
        """Test updating a non-existing TODO."""
        update_data = TodoUpdate(title="Updated Title")
        updated_todo = service.update_todo(999, update_data)
        assert updated_todo is None
    
    def test_update_todo_partial(self, service: TodoService, sample_todo_create: TodoCreate):
        """Test partial TODO update."""
        created_todo = service.create_todo(sample_todo_create)
        
        # Update only the status
        update_data = TodoUpdate(status=TodoStatus.IN_PROGRESS)
        updated_todo = service.update_todo(created_todo.id, update_data)
        
        assert updated_todo.status == TodoStatus.IN_PROGRESS
        assert updated_todo.title == sample_todo_create.title  # Unchanged
        assert updated_todo.description == sample_todo_create.description  # Unchanged
    
    def test_delete_todo_existing(self, service: TodoService, sample_todo_create: TodoCreate):
        """Test deleting an existing TODO."""
        created_todo = service.create_todo(sample_todo_create)
        
        # Delete the TODO
        deleted = service.delete_todo(created_todo.id)
        assert deleted is True
        
        # Verify it's deleted
        retrieved_todo = service.get_todo(created_todo.id)
        assert retrieved_todo is None
    
    def test_delete_todo_non_existing(self, service: TodoService):
        """Test deleting a non-existing TODO."""
        deleted = service.delete_todo(999)
        assert deleted is False
    
    def test_get_stats_empty(self, service: TodoService):
        """Test statistics when no TODOs exist."""
        stats = service.get_stats()
        
        assert stats["total"] == 0
        assert stats["by_status"] == {}
        assert stats["by_priority"] == {}
        assert stats["overdue"] == 0
    
    def test_get_stats_with_data(self, service: TodoService):
        """Test statistics with existing TODOs."""
        # Create TODOs with different statuses and priorities
        service.create_todo(TodoCreate(title="TODO 1", status=TodoStatus.PENDING, priority=TodoPriority.HIGH))
        service.create_todo(TodoCreate(title="TODO 2", status=TodoStatus.IN_PROGRESS, priority=TodoPriority.MEDIUM))
        service.create_todo(TodoCreate(title="TODO 3", status=TodoStatus.COMPLETED, priority=TodoPriority.LOW))
        service.create_todo(TodoCreate(title="TODO 4", status=TodoStatus.PENDING, priority=TodoPriority.HIGH))
        
        stats = service.get_stats()
        
        assert stats["total"] == 4
        assert stats["by_status"]["pending"] == 2
        assert stats["by_status"]["in_progress"] == 1
        assert stats["by_status"]["completed"] == 1
        assert stats["by_priority"]["high"] == 2
        assert stats["by_priority"]["medium"] == 1
        assert stats["by_priority"]["low"] == 1
    
    def test_get_stats_overdue(self, service: TodoService):
        """Test statistics with overdue TODOs."""
        from app.models.todo import Todo
        
        # Create overdue TODO manually (since schema validation prevents past dates)
        overdue_todo = Todo(
            id=1,
            title="Overdue TODO",
            status=TodoStatus.PENDING,
            due_date=datetime.utcnow() - timedelta(days=1)
        )
        service._todos[1] = overdue_todo
        service._next_id = 2
        
        # Create completed overdue TODO (should not count as overdue)
        completed_overdue_todo = Todo(
            id=2,
            title="Completed Overdue TODO",
            status=TodoStatus.COMPLETED,
            due_date=datetime.utcnow() - timedelta(days=1)
        )
        service._todos[2] = completed_overdue_todo
        service._next_id = 3
        
        # Create future TODO
        service.create_todo(TodoCreate(
            title="Future TODO",
            due_date=datetime.utcnow() + timedelta(days=1)
        ))
        
        stats = service.get_stats()
        
        assert stats["total"] == 3
        assert stats["overdue"] == 1  # Only the pending overdue TODO
    
    def test_clear_all(self, service: TodoService):
        """Test clearing all TODOs."""
        # Create some TODOs
        service.create_todo(TodoCreate(title="TODO 1"))
        service.create_todo(TodoCreate(title="TODO 2"))
        
        # Verify they exist
        todos, total = service.get_todos()
        assert total == 2
        
        # Clear all
        service.clear_all()
        
        # Verify they're gone
        todos, total = service.get_todos()
        assert total == 0
        
        # Verify ID counter is reset
        new_todo = service.create_todo(TodoCreate(title="New TODO"))
        assert new_todo.id == 1
