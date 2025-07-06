"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.todo_service import todo_service


@pytest.fixture
def client():
    """Create a test client."""
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_todos():
    """Clean up todos before and after each test."""
    todo_service.clear_all()
    yield
    todo_service.clear_all()


@pytest.fixture
def sample_todo_data():
    """Sample TODO data for testing."""
    return {
        "title": "Test TODO",
        "description": "This is a test TODO item",
        "status": "pending",
        "priority": "medium"
    }


@pytest.fixture
def sample_todos_data():
    """Multiple sample TODOs for testing."""
    return [
        {
            "title": "First TODO",
            "description": "First test TODO",
            "status": "pending",
            "priority": "high"
        },
        {
            "title": "Second TODO",
            "description": "Second test TODO",
            "status": "in_progress",
            "priority": "medium"
        },
        {
            "title": "Third TODO",
            "description": "Third test TODO",
            "status": "completed",
            "priority": "low"
        }
    ]
