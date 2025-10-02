# Common Tasks and Development Workflow

.PHONY: help install lint format type-check test test-cov clean build-lambda run-all

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install dependencies and pre-commit hooks"
	@echo "  lint         - Run code linting with ruff"
	@echo "  format       - Format code with black"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  test         - Run unit tests"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  clean        - Clean build artifacts"
	@echo "  build-lambda - Build Lambda deployment package"
	@echo "  run-all      - Run all quality checks and tests"

# Development setup
install:
	pip install -r requirements.txt
	pip install ruff black mypy pytest pytest-cov pre-commit bandit
	pre-commit install

# Code quality
lint:
	ruff check src/ tests/ bin/

format:
	black src/ tests/ bin/

type-check:
	mypy src/aws_sec_toolkit/

# Testing
test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=src/aws_sec_toolkit --cov-report=html --cov-report=term

# Security scanning
security-scan:
	bandit -r src/ -f json -o bandit-report.json

# Build and deployment
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build-lambda:
	cd infra/lambda && chmod +x build.sh && ./build.sh

# Run individual scripts
run-guardduty:
	python bin/enable_guardduty_all_regions.py

run-securityhub:
	python bin/enable_securityhub_all_regions.py

run-s3-bpa:
	python bin/s3_block_public_access_everywhere.py

run-iam-mfa:
	python bin/iam_enforce_mfa_report_and_disable_keys.py

run-sg-audit:
	python bin/ec2_sg_audit_and_fix_open_ports.py

run-cloudtrail:
	python bin/cloudtrail_enable_multiregion.py

# Comprehensive quality check
run-all: lint format type-check test security-scan
	@echo "All quality checks completed successfully!"

# Documentation
docs-build:
	@echo "Building documentation..."
	@echo "Documentation available in docs/ directory"

# Package build
build-package:
	python -m build

# Development convenience targets
dev-setup: install
	@echo "Development environment setup complete!"

quick-test:
	python -m pytest tests/ -x --tb=short

# CI simulation
ci-test: lint format type-check test security-scan
	@echo "CI checks completed!"