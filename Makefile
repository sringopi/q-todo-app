# TODO API Makefile

.PHONY: install test run clean lint help

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies in virtual environment"
	@echo "  test       - Run all tests"
	@echo "  test-cov   - Run tests with coverage report"
	@echo "  run        - Start the development server"
	@echo "  clean      - Clean up temporary files"
	@echo "  lint       - Run code linting (if flake8 is installed)"
	@echo "  help       - Show this help message"

# Install dependencies
install:
	python3 -m venv ../todo_api_venv
	../todo_api_venv/bin/pip install -r requirements.txt

# Run tests
test:
	../todo_api_venv/bin/python -m pytest -v

# Run tests with coverage
test-cov:
	../todo_api_venv/bin/python -m pytest --cov=app --cov-report=html --cov-report=term

# Start development server
run:
	../todo_api_venv/bin/python run.py

# Clean temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Lint code (optional)
lint:
	../todo_api_venv/bin/python -m flake8 app tests --max-line-length=100
