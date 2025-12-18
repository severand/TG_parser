.PHONY: help install test test-unit test-integration coverage lint format clean

# Variables
PYTHON := python3
PIP := pip3
PROJECT := tg_parser

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help:
	@echo "$(GREEN)TG Parser Makefile Commands$(NC)"
	@echo ""
	@echo "Development:"
	@echo "  make install         - Install dependencies"
	@echo "  make dev-install     - Install dev dependencies"
	@echo "  make clean           - Clean cache and build files"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests only"
	@echo "  make test-integration- Run integration tests only"
	@echo "  make coverage        - Generate coverage report"
	@echo "  make coverage-html   - Generate HTML coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            - Run linters (pylint, flake8)"
	@echo "  make format          - Format code (black, isort)"
	@echo "  make format-check    - Check code format"
	@echo ""
	@echo "Running:"
	@echo "  make run             - Run main CLI"
	@echo "  make run-help        - Show CLI help"

install:
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Done!$(NC)"

dev-install:
	@echo "$(YELLOW)Installing dev dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov pytest-mock black isort pylint flake8
	@echo "$(GREEN)Done!$(NC)"

test:
	@echo "$(YELLOW)Running all tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v --tb=short

test-unit:
	@echo "$(YELLOW)Running unit tests...$(NC)"
	$(PYTHON) -m pytest tests/unit/ -v --tb=short

test-integration:
	@echo "$(YELLOW)Running integration tests...$(NC)"
	$(PYTHON) -m pytest tests/integration/ -v --tb=short

test-quick:
	@echo "$(YELLOW)Running quick tests (no slow)...$(NC)"
	$(PYTHON) -m pytest tests/ -v -m "not slow"

coverage:
	@echo "$(YELLOW)Generating coverage report...$(NC)"
	$(PYTHON) -m pytest --cov=core --cov=network --cov=utils --cov=data --cov=stats --cov=output --cov-report=term-missing

coverage-html:
	@echo "$(YELLOW)Generating HTML coverage report...$(NC)"
	$(PYTHON) -m pytest --cov=core --cov=network --cov=utils --cov=data --cov=stats --cov=output --cov-report=html
	@echo "$(GREEN)Report generated: htmlcov/index.html$(NC)"

coverage-check:
	@echo "$(YELLOW)Checking coverage threshold (80%)...$(NC)"
	$(PYTHON) -m pytest --cov=core --cov=network --cov=utils --cov=data --cov=stats --cov=output --cov-fail-under=80

lint:
	@echo "$(YELLOW)Running linters...$(NC)"
	@echo "Running pylint..."
	$(PYTHON) -m pylint core network utils data stats output main.py --max-line-length=120 || true
	@echo "Running flake8..."
	$(PYTHON) -m flake8 core network utils data stats output main.py --max-line-length=120 || true
	@echo "$(GREEN)Linting complete!$(NC)"

format:
	@echo "$(YELLOW)Formatting code...$(NC)"
	@echo "Running black..."
	$(PYTHON) -m black core network utils data stats output tests main.py
	@echo "Running isort..."
	$(PYTHON) -m isort core network utils data stats output tests main.py
	@echo "$(GREEN)Formatting complete!$(NC)"

format-check:
	@echo "$(YELLOW)Checking code format...$(NC)"
	@echo "Checking black..."
	$(PYTHON) -m black --check core network utils data stats output tests main.py || true
	@echo "Checking isort..."
	$(PYTHON) -m isort --check-only core network utils data stats output tests main.py || true
	@echo "$(GREEN)Format check complete!$(NC)"

clean:
	@echo "$(YELLOW)Cleaning up...$(NC)"
	rm -rf __pycache__ .pytest_cache .coverage htmlcov .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	@echo "$(GREEN)Cleaned!$(NC)"

run:
	@echo "$(YELLOW)Running TG Parser...$(NC)"
	$(PYTHON) main.py --help

run-help:
	@echo "$(YELLOW)Showing CLI help...$(NC)"
	$(PYTHON) main.py --help

run-search:
	@echo "$(YELLOW)Running search example...$(NC)"
	$(PYTHON) main.py search --channels "@python" --keywords "async" --output-format console

setup: install dev-install
	@echo "$(GREEN)Setup complete! Run 'make help' for available commands.$(NC)"

.DEFAULT_GOAL := help
