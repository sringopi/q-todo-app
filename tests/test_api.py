"""
API endpoint tests including edge cases.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient


class TestHealthAndRoot:
    """Test health check and root endpoints."""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data


class TestCreateTodo:
    """Test TODO creation endpoint."""
    
    def test_create_todo_success(self, client: TestClient, sample_todo_data):
        """Test successful TODO creation."""
        response = client.post("/api/v1/todos/", json=sample_todo_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == sample_todo_data["title"]
        assert data["description"] == sample_todo_data["description"]
        assert data["status"] == sample_todo_data["status"]
        assert data["priority"] == sample_todo_data["priority"]
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_todo_minimal_data(self, client: TestClient):
        """Test TODO creation with minimal required data."""
        todo_data = {"title": "Minimal TODO"}
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Minimal TODO"
        assert data["status"] == "pending"
        assert data["priority"] == "medium"
        assert data["description"] is None
    
    def test_create_todo_with_due_date(self, client: TestClient):
        """Test TODO creation with due date."""
        future_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        todo_data = {
            "title": "TODO with due date",
            "due_date": future_date
        }
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["due_date"] is not None
    
    def test_create_todo_empty_title(self, client: TestClient):
        """Test TODO creation with empty title."""
        todo_data = {"title": ""}
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 422
    
    def test_create_todo_whitespace_title(self, client: TestClient):
        """Test TODO creation with whitespace-only title."""
        todo_data = {"title": "   "}
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 422
    
    def test_create_todo_missing_title(self, client: TestClient):
        """Test TODO creation without title."""
        todo_data = {"description": "No title"}
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 422
    
    def test_create_todo_title_too_long(self, client: TestClient):
        """Test TODO creation with title exceeding max length."""
        todo_data = {"title": "x" * 201}  # Max length is 200
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 422
    
    def test_create_todo_description_too_long(self, client: TestClient):
        """Test TODO creation with description exceeding max length."""
        todo_data = {
            "title": "Valid title",
            "description": "x" * 1001  # Max length is 1000
        }
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 422
    
    def test_create_todo_invalid_status(self, client: TestClient):
        """Test TODO creation with invalid status."""
        todo_data = {
            "title": "Valid title",
            "status": "invalid_status"
        }
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 422
    
    def test_create_todo_invalid_priority(self, client: TestClient):
        """Test TODO creation with invalid priority."""
        todo_data = {
            "title": "Valid title",
            "priority": "invalid_priority"
        }
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 422
    
    def test_create_todo_past_due_date(self, client: TestClient):
        """Test TODO creation with past due date."""
        past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
        todo_data = {
            "title": "TODO with past due date",
            "due_date": past_date
        }
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 422
    
    def test_create_todo_invalid_due_date_format(self, client: TestClient):
        """Test TODO creation with invalid due date format."""
        todo_data = {
            "title": "TODO with invalid due date",
            "due_date": "invalid-date-format"
        }
        response = client.post("/api/v1/todos/", json=todo_data)
        assert response.status_code == 422


class TestGetTodos:
    """Test TODO retrieval endpoints."""
    
    def test_get_empty_todos(self, client: TestClient):
        """Test getting TODOs when none exist."""
        response = client.get("/api/v1/todos/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["todos"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 1
    
    def test_get_todos_success(self, client: TestClient, sample_todos_data):
        """Test successful TODO retrieval."""
        # Create test TODOs
        for todo_data in sample_todos_data:
            client.post("/api/v1/todos/", json=todo_data)
        
        response = client.get("/api/v1/todos/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["todos"]) == 3
        assert data["total"] == 3
    
    def test_get_todos_filter_by_status(self, client: TestClient, sample_todos_data):
        """Test TODO filtering by status."""
        # Create test TODOs
        for todo_data in sample_todos_data:
            client.post("/api/v1/todos/", json=todo_data)
        
        response = client.get("/api/v1/todos/?status=pending")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["todos"]) == 1
        assert data["todos"][0]["status"] == "pending"
    
    def test_get_todos_filter_by_priority(self, client: TestClient, sample_todos_data):
        """Test TODO filtering by priority."""
        # Create test TODOs
        for todo_data in sample_todos_data:
            client.post("/api/v1/todos/", json=todo_data)
        
        response = client.get("/api/v1/todos/?priority=high")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["todos"]) == 1
        assert data["todos"][0]["priority"] == "high"
    
    def test_get_todos_pagination(self, client: TestClient):
        """Test TODO pagination."""
        # Create 15 test TODOs
        for i in range(15):
            todo_data = {"title": f"TODO {i+1}"}
            client.post("/api/v1/todos/", json=todo_data)
        
        # Test first page
        response = client.get("/api/v1/todos/?page=1&page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["todos"]) == 5
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert data["total_pages"] == 3
        
        # Test second page
        response = client.get("/api/v1/todos/?page=2&page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["todos"]) == 5
        assert data["page"] == 2
    
    def test_get_todos_invalid_page(self, client: TestClient):
        """Test TODO retrieval with invalid page number."""
        response = client.get("/api/v1/todos/?page=0")
        assert response.status_code == 422
    
    def test_get_todos_invalid_page_size(self, client: TestClient):
        """Test TODO retrieval with invalid page size."""
        response = client.get("/api/v1/todos/?page_size=0")
        assert response.status_code == 422
        
        response = client.get("/api/v1/todos/?page_size=101")  # Max is 100
        assert response.status_code == 422


class TestGetTodoById:
    """Test individual TODO retrieval."""
    
    def test_get_todo_success(self, client: TestClient, sample_todo_data):
        """Test successful TODO retrieval by ID."""
        # Create a TODO
        create_response = client.post("/api/v1/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]
        
        # Get the TODO
        response = client.get(f"/api/v1/todos/{todo_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == sample_todo_data["title"]
    
    def test_get_todo_not_found(self, client: TestClient):
        """Test TODO retrieval with non-existent ID."""
        response = client.get("/api/v1/todos/999")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_todo_invalid_id(self, client: TestClient):
        """Test TODO retrieval with invalid ID."""
        response = client.get("/api/v1/todos/0")
        assert response.status_code == 400
        
        response = client.get("/api/v1/todos/-1")
        assert response.status_code == 400
    
    def test_get_todo_non_integer_id(self, client: TestClient):
        """Test TODO retrieval with non-integer ID."""
        response = client.get("/api/v1/todos/abc")
        assert response.status_code == 422


class TestUpdateTodo:
    """Test TODO update endpoint."""
    
    def test_update_todo_success(self, client: TestClient, sample_todo_data):
        """Test successful TODO update."""
        # Create a TODO
        create_response = client.post("/api/v1/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]
        
        # Update the TODO
        update_data = {
            "title": "Updated TODO",
            "status": "completed"
        }
        response = client.put(f"/api/v1/todos/{todo_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated TODO"
        assert data["status"] == "completed"
        assert data["description"] == sample_todo_data["description"]  # Unchanged
    
    def test_update_todo_partial(self, client: TestClient, sample_todo_data):
        """Test partial TODO update."""
        # Create a TODO
        create_response = client.post("/api/v1/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]
        
        # Update only the status
        update_data = {"status": "in_progress"}
        response = client.put(f"/api/v1/todos/{todo_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["title"] == sample_todo_data["title"]  # Unchanged
    
    def test_update_todo_not_found(self, client: TestClient):
        """Test TODO update with non-existent ID."""
        update_data = {"title": "Updated TODO"}
        response = client.put("/api/v1/todos/999", json=update_data)
        assert response.status_code == 404
    
    def test_update_todo_invalid_id(self, client: TestClient):
        """Test TODO update with invalid ID."""
        update_data = {"title": "Updated TODO"}
        response = client.put("/api/v1/todos/0", json=update_data)
        assert response.status_code == 400
    
    def test_update_todo_empty_title(self, client: TestClient, sample_todo_data):
        """Test TODO update with empty title."""
        # Create a TODO
        create_response = client.post("/api/v1/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]
        
        # Try to update with empty title
        update_data = {"title": ""}
        response = client.put(f"/api/v1/todos/{todo_id}", json=update_data)
        assert response.status_code == 422
    
    def test_update_todo_invalid_status(self, client: TestClient, sample_todo_data):
        """Test TODO update with invalid status."""
        # Create a TODO
        create_response = client.post("/api/v1/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]
        
        # Try to update with invalid status
        update_data = {"status": "invalid_status"}
        response = client.put(f"/api/v1/todos/{todo_id}", json=update_data)
        assert response.status_code == 422


class TestDeleteTodo:
    """Test TODO deletion endpoint."""
    
    def test_delete_todo_success(self, client: TestClient, sample_todo_data):
        """Test successful TODO deletion."""
        # Create a TODO
        create_response = client.post("/api/v1/todos/", json=sample_todo_data)
        todo_id = create_response.json()["id"]
        
        # Delete the TODO
        response = client.delete(f"/api/v1/todos/{todo_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/todos/{todo_id}")
        assert get_response.status_code == 404
    
    def test_delete_todo_not_found(self, client: TestClient):
        """Test TODO deletion with non-existent ID."""
        response = client.delete("/api/v1/todos/999")
        assert response.status_code == 404
    
    def test_delete_todo_invalid_id(self, client: TestClient):
        """Test TODO deletion with invalid ID."""
        response = client.delete("/api/v1/todos/0")
        assert response.status_code == 400


class TestTodoStats:
    """Test TODO statistics endpoint."""
    
    def test_get_stats_empty(self, client: TestClient):
        """Test statistics when no TODOs exist."""
        response = client.get("/api/v1/todos/stats/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 0
        assert data["by_status"] == {}
        assert data["by_priority"] == {}
        assert data["overdue"] == 0
    
    def test_get_stats_with_todos(self, client: TestClient, sample_todos_data):
        """Test statistics with existing TODOs."""
        # Create test TODOs
        for todo_data in sample_todos_data:
            client.post("/api/v1/todos/", json=todo_data)
        
        response = client.get("/api/v1/todos/stats/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 3
        assert data["by_status"]["pending"] == 1
        assert data["by_status"]["in_progress"] == 1
        assert data["by_status"]["completed"] == 1
        assert data["by_priority"]["high"] == 1
        assert data["by_priority"]["medium"] == 1
        assert data["by_priority"]["low"] == 1
    
    def test_get_stats_with_overdue(self, client: TestClient):
        """Test statistics with overdue TODOs."""
        # Create an overdue TODO
        # We need to create this manually since the API validation prevents past dates
        from app.services.todo_service import todo_service
        from app.models.todo import Todo, TodoStatus
        
        # Create overdue TODO directly in service
        overdue_todo = Todo(
            id=1,
            title="Overdue TODO",
            status=TodoStatus.PENDING,
            due_date=datetime.utcnow() - timedelta(days=1)
        )
        todo_service._todos[1] = overdue_todo
        todo_service._next_id = 2
        
        response = client.get("/api/v1/todos/stats/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["overdue"] == 1


class TestEdgeCases:
    """Test various edge cases and error conditions."""
    
    def test_malformed_json(self, client: TestClient):
        """Test API with malformed JSON."""
        response = client.post(
            "/api/v1/todos/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_large_payload(self, client: TestClient):
        """Test API with very large payload."""
        large_data = {
            "title": "Valid title",
            "description": "x" * 999,  # Just under the limit
        }
        response = client.post("/api/v1/todos/", json=large_data)
        assert response.status_code == 201
    
    def test_unicode_content(self, client: TestClient):
        """Test API with Unicode content."""
        unicode_data = {
            "title": "TODO with émojis 🚀 and ünïcödé",
            "description": "Testing with various characters: 中文, العربية, русский"
        }
        response = client.post("/api/v1/todos/", json=unicode_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == unicode_data["title"]
        assert data["description"] == unicode_data["description"]
    
    def test_concurrent_operations(self, client: TestClient):
        """Test concurrent TODO operations."""
        import threading
        import time
        
        results = []
        
        def create_todo(index):
            todo_data = {"title": f"Concurrent TODO {index}"}
            response = client.post("/api/v1/todos/", json=todo_data)
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_todo, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 201 for status in results)
        
        # Verify all TODOs were created
        response = client.get("/api/v1/todos/")
        assert response.json()["total"] == 10
