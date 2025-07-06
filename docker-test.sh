#!/bin/bash

# Docker Test Runner for TODO API
# This script builds and runs tests in Docker containers

set -e

echo "🐳 Docker Test Runner for TODO API"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Clean up function
cleanup() {
    print_status "Cleaning up containers..."
    docker-compose down --remove-orphans 2>/dev/null || true
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Parse command line arguments
COMMAND=${1:-"test"}
COVERAGE=${2:-"true"}

case $COMMAND in
    "build")
        print_status "Building Docker images..."
        docker-compose build
        print_success "Docker images built successfully!"
        ;;
    
    "test")
        print_status "Building test image..."
        docker build -f Dockerfile.test -t todo-api-test .
        
        print_status "Running tests in Docker container..."
        
        # Create test results directory
        mkdir -p test-results
        
        if [ "$COVERAGE" = "true" ]; then
            print_status "Running tests with coverage..."
            docker run --rm \
                -v "$(pwd)/test-results:/app/test-results" \
                -e PYTHONPATH=/app \
                todo-api-test \
                pytest -v \
                --cov=app \
                --cov-report=term \
                --cov-report=html:/app/test-results/htmlcov \
                --junitxml=/app/test-results/junit.xml
        else
            print_status "Running tests without coverage..."
            docker run --rm \
                -v "$(pwd)/test-results:/app/test-results" \
                -e PYTHONPATH=/app \
                todo-api-test \
                pytest -v \
                --junitxml=/app/test-results/junit.xml
        fi
        
        print_success "Tests completed! Results saved to test-results/"
        
        if [ -f "test-results/htmlcov/index.html" ]; then
            print_success "Coverage report available at: test-results/htmlcov/index.html"
        fi
        ;;
    
    "run")
        print_status "Building and starting the application..."
        docker-compose up --build -d todo-api
        
        print_status "Waiting for application to be ready..."
        sleep 5
        
        # Health check
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Application is running at http://localhost:8000"
            print_success "API Documentation: http://localhost:8000/docs"
            print_success "Health Check: http://localhost:8000/health"
        else
            print_error "Application failed to start properly"
            docker-compose logs todo-api
            exit 1
        fi
        ;;
    
    "test-integration")
        print_status "Running integration tests..."
        
        # Start the application
        docker-compose up --build -d todo-api
        
        # Wait for it to be ready
        print_status "Waiting for application to be ready..."
        sleep 10
        
        # Run tests against the running application
        print_status "Running integration tests against running application..."
        docker build -f Dockerfile.test -t todo-api-test .
        
        mkdir -p test-results
        
        docker run --rm \
            --network="$(basename $(pwd))_default" \
            -v "$(pwd)/test-results:/app/test-results" \
            -e PYTHONPATH=/app \
            -e TEST_BASE_URL=http://todo-api:8000 \
            todo-api-test \
            pytest -v tests/test_api.py \
            --junitxml=/app/test-results/junit-integration.xml
        
        print_success "Integration tests completed!"
        ;;
    
    "clean")
        print_status "Cleaning up Docker resources..."
        docker-compose down --remove-orphans --volumes
        docker rmi todo-api-test 2>/dev/null || true
        docker system prune -f
        rm -rf test-results
        print_success "Cleanup completed!"
        ;;
    
    "logs")
        print_status "Showing application logs..."
        docker-compose logs -f todo-api
        ;;
    
    "shell")
        print_status "Opening shell in test container..."
        docker build -f Dockerfile.test -t todo-api-test .
        docker run --rm -it \
            -v "$(pwd):/app" \
            -e PYTHONPATH=/app \
            todo-api-test \
            /bin/bash
        ;;
    
    *)
        echo "Usage: $0 {build|test|run|test-integration|clean|logs|shell}"
        echo ""
        echo "Commands:"
        echo "  build            - Build Docker images"
        echo "  test             - Run tests in Docker (default)"
        echo "  run              - Build and run the application"
        echo "  test-integration - Run integration tests against running app"
        echo "  clean            - Clean up Docker resources"
        echo "  logs             - Show application logs"
        echo "  shell            - Open shell in test container"
        echo ""
        echo "Examples:"
        echo "  $0 test          - Run all tests with coverage"
        echo "  $0 test false    - Run tests without coverage"
        echo "  $0 run           - Start the application"
        exit 1
        ;;
esac
