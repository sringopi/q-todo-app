"""
TODO Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.todo import TodoStatus, TodoPriority


class TodoBase(BaseModel):
    """Base TODO schema."""
    title: str = Field(..., min_length=1, max_length=200, description="TODO title")
    description: Optional[str] = Field(None, max_length=1000, description="TODO description")
    status: TodoStatus = Field(TodoStatus.PENDING, description="TODO status")
    priority: TodoPriority = Field(TodoPriority.MEDIUM, description="TODO priority")
    due_date: Optional[datetime] = Field(None, description="Due date for the TODO")

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        """Validate title is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_strip_whitespace(cls, v):
        """Strip whitespace from description."""
        return v.strip() if v else v

    @field_validator('due_date')
    @classmethod
    def due_date_must_be_future(cls, v):
        """Validate due date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v


class TodoCreate(TodoBase):
    """Schema for creating a TODO."""
    pass


class TodoUpdate(BaseModel):
    """Schema for updating a TODO."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None
    due_date: Optional[datetime] = None

    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        """Validate title is not empty or whitespace only."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip() if v else v

    @field_validator('description')
    @classmethod
    def description_strip_whitespace(cls, v):
        """Strip whitespace from description."""
        return v.strip() if v else v

    @field_validator('due_date')
    @classmethod
    def due_date_must_be_future(cls, v):
        """Validate due date is in the future."""
        if v and v <= datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v


class TodoResponse(TodoBase):
    """Schema for TODO response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="TODO ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TodoListResponse(BaseModel):
    """Schema for TODO list response."""
    todos: List[TodoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    error_code: Optional[str] = None
