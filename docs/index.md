# AWS Security Toolkit

A comprehensive toolkit for hardening AWS environments with automated security controls and compliance checks.

## Overview

The AWS Security Toolkit provides a unified interface for managing essential AWS security services across your environment. Whether you're implementing security best practices for the first time or maintaining ongoing compliance, this toolkit streamlines the process with both command-line tools and Python APIs.

## Key Features

- **Multi-region support** - Operate across all AWS regions simultaneously
- **Dry-run mode** - Preview changes before applying them
- **Multiple output formats** - Table, JSON, and CSV output options
- **Unified CLI** - Single command interface for all security tools
- **Individual scripts** - Standalone scripts for specific tasks
- **Role assumption** - Support for cross-account operations

## Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/buffnerd/AWS-Security-Hardening.git
cd AWS-Security-Hardening
pip install -e .

# Or install development dependencies
pip install -e ".[dev]"
```

### Basic Usage

```bash
# Using the unified CLI
awssec guardduty enable --dry-run
awssec s3-bpa enforce --apply
awssec iam-mfa report --output json

# Using individual scripts
python scripts/guardduty_enable.py --apply
python scripts/s3_block_public_access.py --dry-run
```

### Configuration

Configure AWS credentials using any of the standard methods:
- AWS CLI (`aws configure`)
- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- IAM roles (for EC2 instances)
- AWS profiles (`--profile` flag)

## Utility Index

| Tool | Description | CLI Command | Script Path | Documentation |
|------|-------------|-------------|-------------|---------------|
| **CloudTrail** | Enable & validate multi-region CloudTrail | `awssec cloudtrail enable` | [`scripts/cloudtrail_enable.py`](scripts/cloudtrail_enable.py) | [docs/tools/cloudtrail.md](docs/tools/cloudtrail.md) |
| **GuardDuty** | Enable threat detection across all regions | `awssec guardduty enable` | [`scripts/guardduty_enable.py`](scripts/guardduty_enable.py) | [docs/tools/guardduty.md](docs/tools/guardduty.md) |
| **Security Hub** | Enable Security Hub + standards | `awssec securityhub enable` | [`scripts/securityhub_enable.py`](scripts/securityhub_enable.py) | [docs/tools/securityhub.md](docs/tools/securityhub.md) |
| **S3 BPA** | Block public access at account & bucket level | `awssec s3-bpa enforce` | [`scripts/s3_block_public_access.py`](scripts/s3_block_public_access.py) | [docs/tools/s3_bpa.md](docs/tools/s3_bpa.md) |
| **IAM MFA** | Report/enforce MFA requirements | `awssec iam-mfa report` | [`scripts/iam_mfa_enforce.py`](scripts/iam_mfa_enforce.py) | [docs/tools/iam_mfa.md](docs/tools/iam_mfa.md) |
| **Security Groups** | Audit and fix risky inbound rules | `awssec sg audit` | [`scripts/security_group_audit_fix.py`](scripts/security_group_audit_fix.py) | [docs/tools/sg_audit.md](docs/tools/sg_audit.md) |

## Common Workflows

### Initial Security Hardening
```bash
# Enable foundational security services
awssec guardduty enable --apply
awssec securityhub enable --apply
awssec cloudtrail enable --apply

# Secure S3 buckets
awssec s3-bpa enforce --apply

# Audit MFA compliance
awssec iam-mfa report
```

### Regular Compliance Checks
```bash
# Check security service status
awssec guardduty status --output json
awssec securityhub status --output json

# Audit security groups
awssec sg audit --output csv

# Generate MFA compliance report
awssec iam-mfa report --output csv
```

### Cross-Account Operations
```bash
# Assume role and run security checks
awssec guardduty status --assume-role-arn arn:aws:iam::123456789012:role/SecurityAuditRole
awssec s3-bpa status --profile security-account
```

## Global Options

All commands support these global options:

- `--profile PROFILE` - AWS profile to use
- `--region REGION` - AWS region to target  
- `--assume-role-arn ARN` - IAM role ARN to assume
- `--dry-run` - Show what would be done without making changes
- `--output {table,json,csv}` - Output format (default: table)
- `--log-level {DEBUG,INFO,WARNING,ERROR}` - Log level (default: INFO)

## Examples

### Enable GuardDuty with dry-run
```bash
awssec guardduty enable --dry-run --regions us-east-1,us-west-2
```

### Generate MFA report in CSV format
```bash
awssec iam-mfa report --output csv > mfa-compliance.csv
```

### Audit security groups across specific regions
```bash
awssec sg audit --regions us-east-1,eu-west-1 --output json
```

### Fix security group rules (dry-run first)
```bash
awssec sg fix --dry-run --regions us-east-1
awssec sg fix --apply --regions us-east-1
```

## Development

### Running Tests
```bash
pytest tests/ -v --cov=src/awssec
```

### Code Quality
```bash
# Format code
black src/ tests/ scripts/

# Lint code
ruff check src/ tests/ scripts/

# Type checking
mypy src/
```

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and ensure all tests pass
6. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/buffnerd/AWS-Security-Hardening/issues)
- **Documentation**: [docs/](docs/)
- **Examples**: [examples/](examples/)