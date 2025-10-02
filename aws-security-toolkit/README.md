# AWS Security Toolkit

[![CI Pipeline](https://github.com/buffnerd/AWS-Security-Hardening/actions/workflows/ci.yml/badge.svg)](https://github.com/buffnerd/AWS-Security-Hardening/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/buffnerd/AWS-Security-Hardening/branch/main/graph/badge.svg)](https://codecov.io/gh/buffnerd/AWS-Security-Hardening)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A comprehensive collection of tools and scripts for implementing AWS security best practices and hardening your AWS environment.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/buffnerd/AWS-Security-Hardening.git
cd AWS-Security-Hardening/aws-security-toolkit

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Run a security script (dry-run mode by default)
python bin/enable_guardduty_all_regions.py

# Apply changes (use --apply flag)
python bin/enable_guardduty_all_regions.py --apply
```

### CLI Examples

```bash
# Enable GuardDuty across all regions
python bin/enable_guardduty_all_regions.py --apply --json

# Generate MFA compliance report
python bin/iam_enforce_mfa_report_and_disable_keys.py --csv mfa-report.csv

# Audit security groups for open ports
python bin/ec2_sg_audit_and_fix_open_ports.py --audit-only --json

# Block S3 public access everywhere  
python bin/s3_block_public_access_everywhere.py --apply

# Enable Security Hub in all regions
python bin/enable_securityhub_all_regions.py --apply

# Enable CloudTrail with custom bucket
python bin/cloudtrail_enable_multiregion.py --apply --bucket my-cloudtrail-bucket
```

## 📋 Overview

The AWS Security Toolkit provides automated security hardening capabilities for:

- **GuardDuty** - Threat detection across all regions
- **Security Hub** - Centralized security posture management
- **S3 Security** - Block public access enforcement
- **IAM Hardening** - MFA enforcement and access key management
- **Network Security** - Security group audit and remediation
- **Logging** - CloudTrail multi-region enablement

## 🏗️ Architecture

```
aws-security-toolkit/
├── src/aws_sec_toolkit/          # Core Python package
│   ├── core/                     # Shared utilities
│   ├── scripts/                  # Security hardening logic
│   └── lambda_handlers/          # Serverless deployment
├── bin/                          # CLI executables
├── infra/                        # Infrastructure as Code
├── docs/                         # Documentation
└── examples/                     # Usage examples
```

## 🛠️ Features

### Command Line Tools

Execute security hardening operations directly:

```bash
# Enable GuardDuty in all regions
python bin/enable_guardduty_all_regions.py

# Enable Security Hub in all regions
python bin/enable_securityhub_all_regions.py

# Block S3 public access everywhere
python bin/s3_block_public_access_everywhere.py

# Enforce IAM MFA and disable non-MFA access keys
python bin/iam_enforce_mfa_report_and_disable_keys.py

# Audit and fix security groups
python bin/ec2_sg_audit_and_fix_open_ports.py

# Enable CloudTrail multi-region logging
python bin/cloudtrail_enable_multiregion.py
```

### Serverless Deployment

Deploy as Lambda functions with EventBridge scheduling:

```bash
# Build Lambda package
cd infra/lambda
./build.sh

# Deploy with CloudFormation
aws cloudformation deploy \
    --template-file ../cfn/scheduler-guardduty.yaml \
    --stack-name security-toolkit-guardduty \
    --capabilities CAPABILITY_IAM
```

### Programmatic Usage

Import and use in your own Python applications:

```python
from aws_sec_toolkit.scripts import guardduty_enable

# Enable GuardDuty programmatically
result = guardduty_enable.enable_guardduty_all_regions()
print(f"GuardDuty enabled in {len(result)} regions")
```

## 📚 Documentation

- [**Hardening Runbook**](docs/hardening-runbook.md) - Safe execution order and rollback procedures
- [**IAM Policies**](docs/least-priv-iam.md) - Ready-to-use least privilege policies
- [**Multi-Account Setup**](docs/org-multi-account.md) - Organization-wide deployment patterns
- [**Security Group Notes**](docs/sg-remediation-notes.md) - Remediation best practices

## 🔧 Installation

### Prerequisites

- Python 3.9 or higher
- AWS CLI configured with appropriate permissions
- boto3 and botocore libraries

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install ruff black mypy pytest pytest-cov pre-commit

# Install pre-commit hooks
pre-commit install

# Run tests
python -m pytest tests/

# Run linting
make lint
```

## 🔐 Security Considerations

### Required Permissions

The toolkit requires specific IAM permissions for each service. See [least-priv-iam.md](docs/least-priv-iam.md) for detailed policy examples.

### Safety Features

- **Dry-run mode** for testing changes
- **Rollback procedures** for all operations
- **Incremental deployment** options
- **Comprehensive logging** and monitoring

### Best Practices

1. **Test in non-production first**
2. **Review the hardening runbook**
3. **Backup configurations before changes**
4. **Monitor for service disruptions**
5. **Use least privilege IAM policies**

## 🚀 Usage Examples

### Single Region Operations

```python
from aws_sec_toolkit.core import aws
from aws_sec_toolkit.scripts import guardduty_enable

# Configure for specific region
client = aws.get_aws_client('guardduty', region='us-west-2')
result = guardduty_enable.enable_guardduty_region('us-west-2')
```

### Multi-Account Deployment

```python
from aws_sec_toolkit.core import regions

# Get all enabled regions
enabled_regions = regions.get_enabled_regions()

# Deploy across all regions
for region in enabled_regions:
    result = guardduty_enable.enable_guardduty_region(region)
    print(f"GuardDuty enabled in {region}: {result}")
```

### Error Handling

```python
from aws_sec_toolkit.core import aws
from botocore.exceptions import ClientError

try:
    result = guardduty_enable.enable_guardduty_all_regions()
except ClientError as e:
    aws.handle_aws_error(e)
```

## 📊 Monitoring and Reporting

### Built-in Reports

- IAM users without MFA
- Security groups with open ports
- S3 buckets with public access
- GuardDuty findings summary
- Security Hub compliance scores

### Integration Options

- **CloudWatch Logs** - Centralized logging
- **SNS Notifications** - Alert on security changes
- **Slack Integration** - Team notifications
- **Email Reports** - Scheduled compliance reports

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Code Quality

We maintain high code quality standards:

- **Ruff** for linting and import sorting
- **Black** for code formatting
- **mypy** for type checking
- **pytest** for testing
- **pre-commit** hooks for automation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/buffnerd/AWS-Security-Hardening/issues)
- **Documentation**: [docs/](docs/) directory
- **Examples**: [examples/](examples/) directory
- **Email**: security@yourcompany.com

## 🏷️ Version History

- **v1.0.0** - Initial release with core security hardening features
- See [releases](https://github.com/buffnerd/AWS-Security-Hardening/releases) for detailed changelog

## ⚠️ Disclaimer

This toolkit modifies AWS security settings. Always:

1. **Test thoroughly in non-production environments**
2. **Review all changes before applying to production**
3. **Maintain proper backups and rollback procedures**
4. **Monitor for service disruptions after deployment**

Use at your own risk. The authors are not responsible for any service disruptions or security incidents resulting from the use of this toolkit.

---

**Built with ❤️ for AWS security professionals**