# CloudTrail Security Tool

Enables and validates AWS CloudTrail configuration across all regions to ensure comprehensive API logging and compliance.

## Overview

CloudTrail is essential for security monitoring and compliance as it logs all API calls made in your AWS account. This tool automates the process of enabling CloudTrail with security best practices across all AWS regions.

## Features

- **Multi-region CloudTrail**: Automatically configures CloudTrail to log events from all AWS regions
- **S3 bucket creation**: Creates a secure S3 bucket for log storage with encryption and access controls
- **Log file validation**: Enables log file integrity validation to detect tampering
- **SNS notifications**: Optional SNS topic creation for real-time log delivery notifications
- **KMS encryption**: Encrypts CloudTrail logs using AWS KMS for additional security
- **Dry-run support**: Preview changes before applying them

## Usage

### Unified CLI

```bash
# Enable CloudTrail with dry-run
awssec cloudtrail enable --dry-run

# Enable CloudTrail with changes applied
awssec cloudtrail enable --apply

# Check CloudTrail status
awssec cloudtrail status

# Enable in specific regions only
awssec cloudtrail enable --regions us-east-1,us-west-2 --apply
```

### Standalone Script

```bash
# Enable CloudTrail
python scripts/cloudtrail_enable.py --apply

# Dry-run mode
python scripts/cloudtrail_enable.py --dry-run

# Check status only
python scripts/cloudtrail_enable.py --status-only
```

### Python API

```python
from awssec.tools.cloudtrail import enable_cloudtrail, check_cloudtrail_status

# Enable CloudTrail
results = enable_cloudtrail(
    regions=['us-east-1', 'us-west-2'],
    dry_run=False,
    trail_name='security-audit-trail'
)

# Check status
status = check_cloudtrail_status()
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--apply` | Apply changes (required unless --dry-run) | `False` |
| `--dry-run` | Show what would be done without making changes | `False` |
| `--status-only` | Only check current CloudTrail status | `False` |
| `--regions REGIONS` | Comma-separated list of regions | All regions |
| `--trail-name NAME` | CloudTrail trail name | `security-audit-trail` |
| `--bucket-name NAME` | S3 bucket name for logs | Auto-generated |
| `--sns-topic NAME` | SNS topic name for notifications | None |
| `--kms-key-id ID` | KMS key ID for log encryption | None |

## IAM Permissions Required

The following IAM permissions are required to run this tool:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudtrail:CreateTrail",
                "cloudtrail:DescribeTrails",
                "cloudtrail:GetTrailStatus",
                "cloudtrail:StartLogging",
                "cloudtrail:PutEventSelectors",
                "cloudtrail:UpdateTrail"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:GetBucketLocation",
                "s3:GetBucketPolicy",
                "s3:PutBucketPolicy",
                "s3:PutBucketPublicAccessBlock",
                "s3:PutBucketEncryption",
                "s3:PutBucketVersioning",
                "s3:PutBucketNotification"
            ],
            "Resource": [
                "arn:aws:s3:::cloudtrail-logs-*",
                "arn:aws:s3:::cloudtrail-logs-*/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "sns:CreateTopic",
                "sns:GetTopicAttributes",
                "sns:SetTopicAttributes"
            ],
            "Resource": "arn:aws:sns:*:*:cloudtrail-*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "kms:CreateKey",
                "kms:DescribeKey",
                "kms:GetKeyPolicy",
                "kms:PutKeyPolicy"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": "arn:aws:iam::*:role/CloudTrail_CloudWatchLogsRole"
        }
    ]
}
```

## Security Configuration

The CloudTrail configuration implements the following security best practices:

### S3 Bucket Security
- **Public access blocked**: All public access to the bucket is blocked
- **Server-side encryption**: Logs are encrypted at rest using SSE-S3 or KMS
- **Bucket policy**: Restrictive bucket policy allowing only CloudTrail access
- **Versioning enabled**: Object versioning is enabled for log integrity
- **Lifecycle policies**: Automatic cleanup of old logs (configurable)

### CloudTrail Settings
- **Multi-region**: Captures events from all AWS regions
- **Global services**: Includes global service events (IAM, CloudFront, etc.)
- **Log file validation**: Enables integrity checking of log files
- **Event history**: Captures both management and data events (configurable)
- **Insights**: Optionally enable CloudTrail Insights for anomaly detection

### Access Controls
- **IAM policies**: Restrictive IAM policies for CloudTrail service access
- **Cross-account access**: Proper configuration for multi-account scenarios
- **Least privilege**: Minimum required permissions for log delivery

## Output Examples

### Dry-run Output
```
═══════════════════════════════════════════════════════════════════════════════
                           🛡️  CLOUDTRAIL ENABLER 🛡️                           
                      Multi-region CloudTrail configuration                     
═══════════════════════════════════════════════════════════════════════════════

[DRY-RUN MODE] CloudTrail Configuration Preview

📊 ANALYSIS RESULTS:
┌─────────────────┬─────────────────────────────────────────────────────────┐
│ Region          │ Status                                                  │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ us-east-1       │ ❌ No CloudTrail found - would create new trail         │
│ us-west-2       │ ⚠️  Trail exists but logging disabled - would enable   │
│ eu-west-1       │ ✅ CloudTrail properly configured                       │
└─────────────────┴─────────────────────────────────────────────────────────┘

🔧 PLANNED ACTIONS:
  ✅ Create S3 bucket: cloudtrail-logs-123456789012-us-east-1
  ✅ Configure bucket policy and encryption
  ✅ Create CloudTrail: security-audit-trail
  ✅ Enable logging in us-east-1, us-west-2
  ✅ Configure event selectors for management events

💰 ESTIMATED COSTS:
  • CloudTrail: $2.00/month per trail
  • S3 storage: ~$0.023/GB/month
  • Data events: $0.10 per 100,000 events (if enabled)

🔄 Run with --apply to implement these changes
```

### Apply Output
```
═══════════════════════════════════════════════════════════════════════════════
                           🛡️  CLOUDTRAIL ENABLER 🛡️                           
                      Multi-region CloudTrail configuration                     
═══════════════════════════════════════════════════════════════════════════════

✅ CloudTrail Configuration Complete

📊 RESULTS SUMMARY:
┌─────────────────┬─────────────────────────────────────────────────────────┐
│ Region          │ Status                                                  │
├─────────────────┼─────────────────────────────────────────────────────────┤
│ us-east-1       │ ✅ CloudTrail created and logging enabled               │
│ us-west-2       │ ✅ Logging enabled for existing trail                   │
│ eu-west-1       │ ✅ Already configured properly                          │
└─────────────────┴─────────────────────────────────────────────────────────┘

🔧 ACTIONS COMPLETED:
  ✅ Created S3 bucket: cloudtrail-logs-123456789012-us-east-1
  ✅ Applied bucket policy and encryption
  ✅ Created CloudTrail: security-audit-trail
  ✅ Enabled logging in 2 regions
  ✅ Configured log file validation

📈 NEXT STEPS:
  • Configure CloudWatch Logs delivery for real-time monitoring
  • Set up CloudTrail Insights for anomaly detection
  • Review and customize event selectors for data events
```

## Troubleshooting

### Common Issues

**1. Permission Denied Errors**
```
Error: Access Denied when creating CloudTrail
```
**Solution**: Ensure the IAM user/role has the required CloudTrail permissions listed above.

**2. S3 Bucket Already Exists**
```
Error: Bucket name already exists
```
**Solution**: Use the `--bucket-name` option to specify a unique bucket name.

**3. Trail Already Exists**
```
Error: Trail already exists in region
```
**Solution**: The tool will update existing trails. Use `--status-only` to check current configuration.

**4. Cross-Account Issues**
```
Error: Cannot assume role in target account
```
**Solution**: Verify the assume role permissions and trust relationship.

### Validation Commands

```bash
# Check CloudTrail status across all regions
aws cloudtrail describe-trails --region us-east-1

# Verify logging is enabled
aws cloudtrail get-trail-status --name security-audit-trail

# Check S3 bucket configuration
aws s3api get-bucket-policy --bucket cloudtrail-logs-123456789012-us-east-1
```

## Integration Examples

### With AWS Config
```bash
# Enable CloudTrail before AWS Config for complete audit trail
awssec cloudtrail enable --apply
awssec config enable --apply
```

### With Security Hub
```bash
# CloudTrail findings will appear in Security Hub
awssec cloudtrail enable --apply
awssec securityhub enable --apply
```

### Automated Deployment
```bash
#!/bin/bash
# Multi-account CloudTrail deployment script

ACCOUNTS=("123456789012" "234567890123" "345678901234")
ROLE_NAME="OrganizationAccountAccessRole"

for ACCOUNT in "${ACCOUNTS[@]}"; do
    echo "Configuring CloudTrail for account: $ACCOUNT"
    awssec cloudtrail enable \
        --assume-role-arn "arn:aws:iam::${ACCOUNT}:role/${ROLE_NAME}" \
        --apply
done
```

## Related Tools

- **GuardDuty**: Uses CloudTrail logs for threat detection
- **Security Hub**: Aggregates CloudTrail-based security findings
- **Config**: Leverages CloudTrail for configuration change tracking
- **S3 BPA**: Secures the S3 buckets used for CloudTrail log storage