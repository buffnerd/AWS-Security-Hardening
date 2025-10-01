# AWS Security Hardening Toolbox - Usage Guide

## Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/buffnerd/AWS-Security-Hardening.git
cd AWS-Security-Hardening

# Install Python dependencies
pip install -r requirements.txt

# Verify AWS credentials are configured
aws sts get-caller-identity
```

### 2. Understanding the Structure

The repository is organized by AWS service category:

```
scripts/
├── guardduty/      # Threat detection
├── iam/            # Identity & access management
├── s3/             # Storage security
├── vpc/            # Network security
├── cloudtrail/     # Audit logging
├── config/         # Configuration compliance
├── securityhub/    # Centralized security
├── kms/            # Encryption keys
├── ec2/            # Compute security
└── lambda/         # Serverless security
```

Each directory contains:
- Python scripts for automation
- README.md with documentation
- Usage examples

### 3. Running Scripts

Most scripts follow a common pattern:

```bash
# Basic usage
python scripts/<category>/<script_name>.py

# With AWS profile
python scripts/<category>/<script_name>.py --profile production

# Dry-run mode (recommended first)
python scripts/<category>/<script_name>.py --dry-run

# Specific regions
python scripts/<category>/<script_name>.py --regions us-east-1,eu-west-1

# Debug logging
python scripts/<category>/<script_name>.py --log-level DEBUG
```

## Best Practices

### Testing

1. **Always use dry-run mode first**: Most scripts support `--dry-run` to show what would be done
2. **Test in a non-production account**: Validate scripts in dev/test environments
3. **Review the output**: Check logs carefully before running in production

### Security

1. **Use IAM roles**: Prefer IAM roles over access keys when possible
2. **Least privilege**: Use specific IAM policies, not `AdministratorAccess`
3. **MFA**: Enable MFA on accounts used to run these scripts
4. **Audit logs**: Monitor CloudTrail for script execution

### Execution

1. **Start with one region**: Use `--regions` to test in a single region first
2. **Check prerequisites**: Review the README in each category for required permissions
3. **Monitor execution**: Watch for errors and warnings in the output
4. **Save logs**: Redirect output to files for audit purposes

## Common Workflows

### Initial Account Hardening

1. Enable GuardDuty in all regions:
   ```bash
   python scripts/guardduty/enable_guardduty.py
   ```

2. Enable CloudTrail logging:
   ```bash
   python scripts/cloudtrail/enable_cloudtrail.py
   ```

3. Block public S3 access:
   ```bash
   python scripts/s3/block_public_access.py
   ```

4. Audit IAM configuration:
   ```bash
   python scripts/iam/audit_password_policy.py
   python scripts/iam/audit_mfa_compliance.py
   ```

### Regular Compliance Checks

Run these scripts periodically to maintain security posture:

```bash
# Weekly
python scripts/iam/audit_access_keys.py
python scripts/s3/audit_public_buckets.py

# Monthly
python scripts/iam/audit_unused_roles.py
python scripts/ec2/audit_security_groups.py
```

### Multi-Account Management

For AWS Organizations with multiple accounts:

1. Use AWS Organizations APIs to list accounts
2. Iterate through accounts using `--profile` or assume role
3. Aggregate results for centralized reporting

Example:
```bash
for profile in dev staging prod; do
  echo "Processing account: $profile"
  python scripts/guardduty/enable_guardduty.py --profile $profile
done
```

## Troubleshooting

### Common Issues

**"Access Denied" errors**
- Check IAM permissions
- Verify the role/user has necessary permissions
- Review the README for required permissions

**"Region not enabled" errors**
- Some regions may not be enabled in your account
- Use `--regions` to specify only enabled regions
- Or enable regions in AWS Console first

**Script timeouts**
- Some operations (especially multi-region) can take time
- Scripts log progress - be patient
- Consider processing fewer regions at once

### Getting Help

1. Check the category-specific README
2. Run with `--help` for script options
3. Use `--log-level DEBUG` for detailed information
4. Review AWS service documentation

## Advanced Usage

### Custom Scripting

You can use the utility functions in your own scripts:

```python
import sys
sys.path.append('..')
from utils import get_aws_session, get_enabled_regions

session = get_aws_session(profile='production')
regions = get_enabled_regions(session)

# Your custom logic here
```

### Automation

Integrate scripts into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Security Hardening
  run: |
    python scripts/s3/audit_bucket_encryption.py
    python scripts/iam/audit_mfa_compliance.py
```

### Reporting

Capture output for compliance reports:

```bash
python scripts/iam/audit_password_policy.py > reports/iam_audit_$(date +%Y%m%d).log
```

## Contributing Scripts

When adding new scripts:

1. Place in appropriate category directory
2. Follow existing script patterns
3. Include proper error handling
4. Add documentation to category README
5. Test thoroughly before committing

## Security Considerations

⚠️ **Important Reminders:**

- Never commit AWS credentials
- Test changes in non-production first
- Review all actions before applying
- Keep audit logs of script execution
- Follow your organization's change management process
- Understand the impact of each script before running
