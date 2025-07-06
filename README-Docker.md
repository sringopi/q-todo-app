# Docker Setup for TODO API

This document provides comprehensive instructions for running the TODO API using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- curl (for health checks)

## Quick Start

### 1. Build and Test

```bash
# Build Docker images
./docker-test.sh build

# Run tests in Docker
./docker-test.sh test

# Run application
./docker-test.sh run
```

### 2. Using Make Commands

```bash
# Build Docker images
make docker-build

# Run tests
make docker-test

# Run application
make docker-run

# Clean up
make docker-clean
```

## Docker Commands Reference

### Available Scripts

The `docker-test.sh` script provides several commands:

| Command | Description |
|---------|-------------|
| `build` | Build Docker images |
| `test` | Run tests with coverage |
| `run` | Start the application |
| `test-integration` | Run integration tests against running app |
| `clean` | Clean up Docker resources |
| `logs` | Show application logs |
| `shell` | Open interactive shell in test container |

### Examples

```bash
# Run tests without coverage
./docker-test.sh test false

# Run only integration tests
./docker-test.sh test-integration

# View application logs
./docker-test.sh logs

# Open shell for debugging
./docker-test.sh shell

# Clean up everything
./docker-test.sh clean
```

## Docker Compose Services

### todo-api
- **Purpose**: Main application service
- **Port**: 8000
- **Health Check**: `/health` endpoint
- **Environment**: Development mode enabled

### todo-api-test
- **Purpose**: Test execution service
- **Volumes**: Test results mounted to `./test-results/`
- **Coverage**: HTML and terminal reports

## File Structure

```
todo_api/
├── Dockerfile              # Production image
├── Dockerfile.test         # Test image with additional tools
├── docker-compose.yml      # Multi-service setup
├── docker-test.sh         # Test automation script
├── .dockerignore          # Docker build exclusions
└── test-results/          # Test output directory (created automatically)
    ├── htmlcov/           # Coverage HTML reports
    └── junit.xml          # JUnit test results
```

## Docker Images

### Production Image (Dockerfile)
- **Base**: python:3.11-slim
- **User**: Non-root user (appuser)
- **Port**: 8000
- **Health Check**: Built-in curl health check
- **Security**: Minimal attack surface

### Test Image (Dockerfile.test)
- **Base**: python:3.11-slim
- **Additional Tools**: pytest-cov, pytest-html, pytest-xdist
- **Purpose**: Isolated test execution
- **Output**: Structured test results

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `true` | Enable debug mode |
| `PYTHONPATH` | `/app` | Python module path |
| `PYTHONDONTWRITEBYTECODE` | `1` | Prevent .pyc files |
| `PYTHONUNBUFFERED` | `1` | Force stdout/stderr unbuffered |

## Health Checks

### Application Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Docker Health Check
The Docker container includes built-in health checks:
- **Interval**: 30 seconds
- **Timeout**: 30 seconds
- **Retries**: 3
- **Start Period**: 5 seconds

## Test Results

Test results are automatically saved to `./test-results/`:

- **junit.xml**: JUnit format for CI/CD integration
- **htmlcov/index.html**: Interactive coverage report
- **Terminal output**: Real-time test results

### Viewing Coverage Report

```bash
# After running tests
open test-results/htmlcov/index.html  # macOS
xdg-open test-results/htmlcov/index.html  # Linux
```

## Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Find and kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Docker daemon not running**
   ```bash
   # Start Docker service
   sudo systemctl start docker  # Linux
   # Or start Docker Desktop
   ```

3. **Permission denied on docker-test.sh**
   ```bash
   chmod +x docker-test.sh
   ```

4. **Container fails to start**
   ```bash
   # Check logs
   ./docker-test.sh logs
   
   # Or use docker-compose
   docker-compose logs todo-api
   ```

### Debug Mode

Open an interactive shell in the test container:

```bash
./docker-test.sh shell

# Inside container
pytest -v tests/test_api.py  # Run specific tests
python -m app.main          # Start app manually
curl http://localhost:8000/health  # Test endpoints
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Docker Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and test
        run: |
          cd todo_api
          ./docker-test.sh test
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: todo_api/test-results/
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                dir('todo_api') {
                    sh './docker-test.sh test'
                }
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'todo_api/test-results/htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }
    }
}
```

## Performance Considerations

### Build Optimization
- Multi-stage builds for smaller production images
- Layer caching with requirements.txt
- .dockerignore to exclude unnecessary files

### Runtime Optimization
- Non-root user for security
- Health checks for reliability
- Resource limits (can be added to docker-compose.yml)

### Example Resource Limits

```yaml
# Add to docker-compose.yml services
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 256M
```

## Security Best Practices

1. **Non-root user**: All containers run as non-root
2. **Minimal base image**: Using slim Python image
3. **No secrets in images**: Environment variables for configuration
4. **Health checks**: Automatic failure detection
5. **Resource limits**: Prevent resource exhaustion

## Next Steps

- Add database service to docker-compose.yml
- Implement multi-stage builds for production
- Add monitoring and logging services
- Configure reverse proxy (nginx)
- Set up container orchestration (Kubernetes)
