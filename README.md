# TODO API

A comprehensive TODO API built with FastAPI, featuring full CRUD operations, filtering, pagination, and comprehensive testing.

## Features

- ✅ Create, read, update, and delete TODO items
- ✅ Filter TODOs by status and priority
- ✅ Pagination support
- ✅ Input validation with Pydantic
- ✅ Comprehensive error handling
- ✅ Statistics endpoint
- ✅ Health check endpoint
- ✅ Interactive API documentation (Swagger UI)
- ✅ Comprehensive test suite with edge cases
- ✅ Clean architecture with separation of concerns

## Project Structure

```
todo_api/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Application configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── todo.py            # TODO data models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── todo.py            # Pydantic schemas for validation
│   ├── services/
│   │   ├── __init__.py
│   │   └── todo_service.py    # Business logic layer
│   ├── routers/
│   │   ├── __init__.py
│   │   └── todos.py           # API route handlers
│   ├── __init__.py
│   └── main.py                # FastAPI application setup
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test configuration and fixtures
│   ├── test_api.py            # API endpoint tests
│   ├── test_models.py         # Model tests
│   └── test_services.py       # Service layer tests
├── requirements.txt           # Python dependencies
├── pytest.ini               # Pytest configuration
└── README.md                 # This file
```

## Installation and Setup

### 1. Create and activate virtual environment

```bash
python3 -m venv todo_api_venv
source todo_api_venv/bin/activate  # On Windows: todo_api_venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m app.main
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API information |
| GET | `/health` | Health check endpoint |

### TODO Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/todos/` | Create a new TODO |
| GET | `/api/v1/todos/` | Get all TODOs (with filtering and pagination) |
| GET | `/api/v1/todos/{id}` | Get a specific TODO by ID |
| PUT | `/api/v1/todos/{id}` | Update a TODO |
| DELETE | `/api/v1/todos/{id}` | Delete a TODO |
| GET | `/api/v1/todos/stats/summary` | Get TODO statistics |

### Query Parameters for GET /api/v1/todos/

- `status`: Filter by status (`pending`, `in_progress`, `completed`)
- `priority`: Filter by priority (`low`, `medium`, `high`)
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)

## Data Models

### TODO Item

```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive README and API documentation",
  "status": "pending",
  "priority": "high",
  "created_at": "2025-07-06T06:00:00Z",
  "updated_at": "2025-07-06T06:00:00Z",
  "due_date": "2025-07-13T06:00:00Z"
}
```

### Status Values
- `pending`: TODO is not started
- `in_progress`: TODO is being worked on
- `completed`: TODO is finished

### Priority Values
- `low`: Low priority
- `medium`: Medium priority
- `high`: High priority

## Example Usage

### Create a TODO

```bash
curl -X POST "http://localhost:8000/api/v1/todos/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Complete FastAPI tutorial and build a project",
    "priority": "high",
    "due_date": "2025-07-13T06:00:00Z"
  }'
```

### Get all TODOs with filtering

```bash
# Get all pending TODOs
curl "http://localhost:8000/api/v1/todos/?status=pending"

# Get high priority TODOs with pagination
curl "http://localhost:8000/api/v1/todos/?priority=high&page=1&page_size=5"
```

### Update a TODO

```bash
curl -X PUT "http://localhost:8000/api/v1/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

### Get statistics

```bash
curl "http://localhost:8000/api/v1/todos/stats/summary"
```

## Testing

The project includes comprehensive tests covering:

- ✅ Unit tests for models and services
- ✅ Integration tests for API endpoints
- ✅ Edge cases and error conditions
- ✅ Input validation testing
- ✅ Concurrent operations testing
- ✅ Unicode content testing

### Run all tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=app --cov-report=html
```

### Run specific test categories

```bash
# Run only API tests
pytest tests/test_api.py

# Run only service tests
pytest tests/test_services.py

# Run only model tests
pytest tests/test_models.py
```

### Test Categories

The test suite includes:

1. **Happy Path Tests**: Normal operation scenarios
2. **Edge Cases**: Boundary conditions and unusual inputs
3. **Error Handling**: Invalid inputs and error conditions
4. **Validation Tests**: Input validation and data integrity
5. **Concurrency Tests**: Multi-threaded operations
6. **Performance Tests**: Large payloads and pagination

## Architecture

The application follows clean architecture principles:

### Layers

1. **Presentation Layer** (`routers/`): FastAPI route handlers
2. **Business Logic Layer** (`services/`): Core business logic
3. **Data Layer** (`models/`): Data models and structures
4. **Schema Layer** (`schemas/`): Input/output validation

### Key Design Decisions

- **In-memory storage**: Simple dictionary-based storage for demonstration
- **Pydantic validation**: Comprehensive input validation
- **Service layer**: Business logic separated from API handlers
- **Comprehensive testing**: High test coverage with edge cases
- **Error handling**: Proper HTTP status codes and error messages

## Development

### Code Style

The project follows Python best practices:

- Type hints throughout the codebase
- Comprehensive docstrings
- Clean separation of concerns
- Proper error handling
- Comprehensive testing

### Adding New Features

1. Add models in `app/models/`
2. Create/update schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Add API endpoints in `app/routers/`
5. Write comprehensive tests

## Production Considerations

For production deployment, consider:

- **Database**: Replace in-memory storage with PostgreSQL/MySQL
- **Authentication**: Add JWT or OAuth2 authentication
- **Rate limiting**: Implement API rate limiting
- **Logging**: Add structured logging
- **Monitoring**: Add health checks and metrics
- **Caching**: Implement Redis caching for performance
- **Documentation**: API versioning strategy

## License

This project is for educational purposes and demonstration of FastAPI best practices.
