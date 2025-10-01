# Contributing to AWS Security Hardening Toolbox

Thank you for your interest in contributing! This guide will help you add new scripts and improvements to the repository.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a feature branch
4. Make your changes
5. Submit a pull request

## Repository Organization

### Directory Structure

All security scripts should be placed in category-specific directories under `scripts/`:

```
scripts/
├── guardduty/      # GuardDuty scripts
├── iam/            # IAM scripts
├── s3/             # S3 scripts
├── vpc/            # VPC scripts
├── cloudtrail/     # CloudTrail scripts
├── config/         # AWS Config scripts
├── securityhub/    # Security Hub scripts
├── kms/            # KMS scripts
├── ec2/            # EC2 scripts
└── lambda/         # Lambda scripts
```

If your script doesn't fit an existing category, propose a new one!

## Script Guidelines

### Required Elements

Every script should include:

1. **Shebang line**: `#!/usr/bin/env python3`
2. **Docstring**: Clear description and usage examples
3. **Imports**: Use the shared utilities from `utils/`
4. **Argument parsing**: Support common flags (`--profile`, `--dry-run`, etc.)
5. **Logging**: Use the logging utilities
6. **Error handling**: Catch and handle AWS exceptions properly

### Template Structure

```python
#!/usr/bin/env python3
"""
Brief description of what the script does.

Usage:
    python script_name.py [options]

Options:
    --profile PROFILE   AWS CLI profile to use
    --dry-run          Show what would be done
    --regions REGIONS  Comma-separated list of regions
"""

import sys
import argparse
import logging
sys.path.append('..')
from utils import (
    setup_logging,
    get_aws_session,
    get_enabled_regions,
    handle_aws_error
)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Script description')
    parser.add_argument('--profile', help='AWS CLI profile to use')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    logger = setup_logging(args.log_level)
    
    # Your script logic here
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

### Standard Command-Line Arguments

All scripts should support these common arguments:

- `--profile`: AWS CLI profile to use
- `--dry-run`: Preview mode that doesn't make changes
- `--log-level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `--regions`: Comma-separated list of specific regions

Additional script-specific arguments are welcome!

### Error Handling

Use the utility functions for consistent error handling:

```python
try:
    # AWS API call
    response = client.some_operation()
except Exception as e:
    handle_aws_error(e, "Context about what failed")
```

### Logging

Use the logging utility for consistent output:

```python
logger = setup_logging(args.log_level)
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug details")
```

## Documentation

### Script Documentation

Each script must include:

1. **Docstring** at the top with:
   - Clear description
   - Usage examples
   - Options/arguments

2. **Function docstrings** for all functions:
   ```python
   def function_name(param: str) -> dict:
       """
       Brief description.
       
       Args:
           param: Description of parameter
       
       Returns:
           Description of return value
       """
   ```

### Category Documentation

Update or create `README.md` in the script's category directory:

1. Add your script to the "Available Scripts" section
2. Include:
   - Script name and purpose
   - Usage examples
   - Required IAM permissions
   - Any special considerations

### Main Documentation

For significant additions:

1. Update main `README.md` if adding a new category
2. Update `docs/USAGE.md` with relevant examples
3. Add to examples if creating a new pattern

## Testing

### Before Submitting

1. **Test in dry-run mode**: Verify `--dry-run` works correctly
2. **Test with different arguments**: Try various combinations
3. **Test error conditions**: Verify error handling works
4. **Test in multiple regions**: If multi-region, test region handling
5. **Test with different AWS profiles**: Ensure profile switching works

### Testing Checklist

- [ ] Script runs without errors
- [ ] `--dry-run` mode works correctly
- [ ] Help text is clear (`--help`)
- [ ] Logging is informative
- [ ] Errors are handled gracefully
- [ ] Works with different AWS profiles
- [ ] Documentation is accurate

## Code Style

### Python Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions focused and single-purpose
- Use meaningful variable names
- Maximum line length: 100 characters

### Imports

Organize imports in this order:
```python
# Standard library
import sys
import argparse
import logging

# Third-party
import boto3
from botocore.exceptions import ClientError

# Local utilities
sys.path.append('..')
from utils import setup_logging, get_aws_session
```

## Security Considerations

### Must Follow

1. **Never commit credentials**: Use AWS profiles or IAM roles
2. **Validate inputs**: Sanitize user inputs
3. **Least privilege**: Document minimal IAM permissions needed
4. **Audit logging**: Log all actions taken
5. **Confirmation prompts**: Ask before destructive operations
6. **Dry-run first**: Always implement dry-run mode

### Best Practices

- Use KMS encryption where possible
- Enable CloudTrail logging for auditing
- Follow AWS security best practices
- Document security implications
- Consider multi-account scenarios

## Pull Request Process

1. **Create descriptive PR title**: "Add script to enable S3 encryption"
2. **Describe changes**: Explain what the script does and why
3. **Reference issues**: Link to any related issues
4. **Update documentation**: Include all relevant docs
5. **Test thoroughly**: Provide testing notes

### PR Checklist

- [ ] Script follows template structure
- [ ] Documentation is complete
- [ ] Category README is updated
- [ ] Script has been tested
- [ ] Error handling is implemented
- [ ] Logging is appropriate
- [ ] No credentials in code
- [ ] Code follows style guidelines

## Adding New Categories

To propose a new script category:

1. Create a new directory under `scripts/`
2. Add a `README.md` explaining the category
3. Include at least one example script
4. Update main `README.md`
5. Submit PR with rationale

## Questions?

- Open an issue for discussion
- Review existing scripts for examples
- Check `examples/` directory for patterns

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
