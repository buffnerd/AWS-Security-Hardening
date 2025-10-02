# Contributing to AWS Security Toolkit

Thank you for your interest in contributing to the AWS Security Toolkit! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Style Guide](#style-guide)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to security@yourcompany.com.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/AWS-Security-Hardening.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.9 or higher
- AWS CLI configured with appropriate permissions
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/buffnerd/AWS-Security-Hardening.git
cd AWS-Security-Hardening/aws-security-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install ruff black mypy pytest pytest-cov pre-commit

# Install pre-commit hooks
pre-commit install
```

## Style Guide

### Python Code Style

We use the following tools for code quality:

- **Ruff**: For linting and import sorting
- **Black**: For code formatting
- **mypy**: For type checking

#### Configuration

All tool configurations are defined in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
target-version = "py39"
select = ["E", "W", "F", "I", "N", "B", "UP"]

[tool.black]
line-length = 88
target-version = ['py39']

[tool.mypy]
python_version = "3.9"
strict = true
```

#### Type Hints

- All functions must include type hints
- Use `typing` module for complex types
- Document return types explicitly

```python
from typing import List, Dict, Optional

def process_regions(regions: List[str]) -> Dict[str, bool]:
    """Process AWS regions and return status."""
    pass
```

### Documentation Style

- Use clear, concise language
- Include code examples where appropriate
- Follow Markdown best practices
- Update relevant documentation for any changes

## Commit Guidelines

### Commit Message Format

Use conventional commit format:

```
<type>(<scope>): <description>

<body>

<footer>
```

#### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

#### Examples

```
feat(guardduty): add multi-region enablement support

- Implement region discovery
- Add parallel processing for multiple regions
- Include error handling and retry logic

Closes #123
```

```
fix(s3): handle bucket policy conflicts during BPA enforcement

- Check for existing bucket policies
- Merge instead of overwrite when possible
- Add proper error handling

Fixes #456
```

## Pull Request Process

### Before Submitting

1. **Run tests**: `python -m pytest tests/`
2. **Run linting**: `ruff check src/ tests/ bin/`
3. **Run formatting**: `black src/ tests/ bin/`
4. **Run type checking**: `mypy src/aws_sec_toolkit/`
5. **Update documentation** if needed
6. **Add tests** for new functionality

### PR Requirements

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages follow guidelines
- [ ] No merge conflicts
- [ ] Includes appropriate tests

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added for new functionality
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src/aws_sec_toolkit --cov-report=html

# Run specific test file
python -m pytest tests/test_regions.py

# Run with verbose output
python -m pytest tests/ -v
```

### Test Structure

```
tests/
├── test_regions.py
├── test_cli.py
├── test_aws_helpers.py
├── integration/
│   ├── test_guardduty_integration.py
│   └── test_s3_integration.py
└── fixtures/
    ├── sample_responses.json
    └── test_data.py
```

### Writing Tests

- Use `unittest.mock` for AWS API calls
- Include both positive and negative test cases
- Test error handling and edge cases
- Mock external dependencies

```python
import unittest
from unittest.mock import patch, MagicMock
from aws_sec_toolkit.scripts import guardduty_enable

class TestGuardDutyEnable(unittest.TestCase):
    
    @patch('boto3.client')
    def test_enable_guardduty_success(self, mock_client):
        mock_guardduty = MagicMock()
        mock_client.return_value = mock_guardduty
        mock_guardduty.create_detector.return_value = {'DetectorId': 'test-id'}
        
        result = guardduty_enable.enable_guardduty_all_regions()
        self.assertIsNotNone(result)
```

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings for all functions and classes
2. **User Documentation**: README files and usage guides
3. **API Documentation**: Generated from docstrings
4. **Runbooks**: Operational procedures and troubleshooting

### Docstring Format

Use Google-style docstrings:

```python
def enable_guardduty_region(region: str) -> Dict[str, Any]:
    """Enable GuardDuty in a specific region.
    
    Args:
        region: AWS region name (e.g., 'us-east-1')
        
    Returns:
        Dictionary containing enablement status and detector ID
        
    Raises:
        ClientError: If AWS API call fails
        ValueError: If region is invalid
        
    Example:
        >>> result = enable_guardduty_region('us-east-1')
        >>> print(result['DetectorId'])
        'abc123def456'
    """
```

## Security Considerations

### Code Review Focus Areas

- **Credentials handling**: Never commit secrets
- **IAM permissions**: Follow least privilege principle
- **Input validation**: Sanitize all inputs
- **Error handling**: Don't expose sensitive information
- **Logging**: Avoid logging credentials or sensitive data

### Security Testing

- Run security scans with `bandit`
- Review IAM policies carefully
- Test with minimal permissions
- Validate input sanitization

## Release Process

### Version Numbering

Follow semantic versioning (SemVer):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version bumped in `__init__.py`
- [ ] Changelog updated
- [ ] Git tag created
- [ ] GitHub release created
- [ ] Lambda package built and uploaded

## Questions?

If you have questions about contributing, please:

1. Check existing issues and documentation
2. Create a new issue for discussion
3. Contact the maintainers at security@yourcompany.com

Thank you for contributing to the AWS Security Toolkit!