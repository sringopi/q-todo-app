"""
TODO API routes.
"""
from typing import Optional, Dict, Any
from math import ceil

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from app.schemas.todo import (
    TodoCreate, 
    TodoUpdate, 
    TodoResponse, 
    TodoListResponse,
    ErrorResponse
)
from app.models.todo import TodoStatus, TodoPriority
from app.services.todo_service import todo_service

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post(
    "/",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new TODO",
    description="Create a new TODO item with title, description, status, priority, and due date."
)
async def create_todo(todo: TodoCreate):
    """Create a new TODO item."""
    try:
        created_todo = todo_service.create_todo(todo)
        return TodoResponse(**created_todo.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=TodoListResponse,
    summary="Get all TODOs",
    description="Retrieve all TODO items with optional filtering by status and priority, and pagination support."
)
async def get_todos(
    status: Optional[TodoStatus] = Query(None, description="Filter by status"),
    priority: Optional[TodoPriority] = Query(None, description="Filter by priority"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get all TODOs with optional filtering and pagination."""
    todos, total = todo_service.get_todos(status, priority, page, page_size)
    
    total_pages = ceil(total / page_size) if total > 0 else 1
    
    return TodoListResponse(
        todos=[TodoResponse(**todo.to_dict()) for todo in todos],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Get a TODO by ID",
    description="Retrieve a specific TODO item by its ID.",
    responses={
        404: {"model": ErrorResponse, "description": "TODO not found"}
    }
)
async def get_todo(todo_id: int):
    """Get a specific TODO by ID."""
    if todo_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TODO ID must be a positive integer"
        )
    
    todo = todo_service.get_todo(todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TODO with ID {todo_id} not found"
        )
    
    return TodoResponse(**todo.to_dict())


@router.put(
    "/{todo_id}",
    response_model=TodoResponse,
    summary="Update a TODO",
    description="Update an existing TODO item by its ID.",
    responses={
        404: {"model": ErrorResponse, "description": "TODO not found"}
    }
)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    """Update a TODO item."""
    if todo_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TODO ID must be a positive integer"
        )
    
    try:
        updated_todo = todo_service.update_todo(todo_id, todo_update)
        if not updated_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"TODO with ID {todo_id} not found"
            )
        
        return TodoResponse(**updated_todo.to_dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a TODO",
    description="Delete a TODO item by its ID.",
    responses={
        404: {"model": ErrorResponse, "description": "TODO not found"}
    }
)
async def delete_todo(todo_id: int):
    """Delete a TODO item."""
    if todo_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TODO ID must be a positive integer"
        )
    
    deleted = todo_service.delete_todo(todo_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TODO with ID {todo_id} not found"
        )


@router.get(
    "/stats/summary",
    response_model=Dict[str, Any],
    summary="Get TODO statistics",
    description="Get summary statistics about all TODO items including counts by status, priority, and overdue items."
)
async def get_todo_stats():
    """Get TODO statistics."""
    return todo_service.get_stats()
