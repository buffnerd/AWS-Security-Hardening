# S3 Block Public Access Tool

Enforces S3 Block Public Access settings at both account-level and bucket-level to prevent accidental public exposure of S3 data.

## Overview

S3 Block Public Access is a critical security feature that provides an additional layer of protection against accidental public exposure of S3 objects. This tool automates the enforcement of Block Public Access settings across all S3 buckets and at the account level.

## Features

- **Account-level enforcement**: Applies Block Public Access settings to the entire AWS account
- **Bucket-level enforcement**: Applies settings to individual S3 buckets
- **Multi-region support**: Operates across all AWS regions where S3 is available
- **Selective enforcement**: Option to exclude specific buckets from enforcement
- **Compliance reporting**: Generates reports on current Block Public Access status
- **Dry-run capability**: Preview changes before applying them
- **Override protection**: Prevents accidental disabling of Block Public Access

## Usage

### Unified CLI

```bash
# Enforce Block Public Access with dry-run
awssec s3-bpa enforce --dry-run

# Enforce Block Public Access with changes applied
awssec s3-bpa enforce --apply

# Check current status
awssec s3-bpa status

# Enforce at account level only
awssec s3-bpa enforce --account-level-only --apply

# Exclude specific buckets
awssec s3-bpa enforce --exclude-buckets bucket1,bucket2 --apply
```

### Standalone Script

```bash
# Enforce Block Public Access
python scripts/s3_block_public_access.py --apply

# Dry-run mode
python scripts/s3_block_public_access.py --dry-run

# Check status only
python scripts/s3_block_public_access.py --status-only

# Account level enforcement only
python scripts/s3_block_public_access.py --account-level-only --apply
```

### Python API

```python
from awssec.tools.s3_bpa import enforce_s3_block_public_access, check_s3_bpa_status

# Enforce Block Public Access
results = enforce_s3_block_public_access(
    dry_run=False,
    account_level_only=False,
    exclude_buckets=['public-website-bucket', 'cdn-assets-bucket']
)

# Check status
status = check_s3_bpa_status()
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--apply` | Apply changes (required unless --dry-run) | `False` |
| `--dry-run` | Show what would be done without making changes | `False` |
| `--status-only` | Only check current Block Public Access status | `False` |
| `--account-level-only` | Apply settings only at account level | `False` |
| `--bucket-level-only` | Apply settings only at bucket level | `False` |
| `--exclude-buckets BUCKETS` | Comma-separated list of buckets to exclude | None |
| `--include-buckets BUCKETS` | Comma-separated list of buckets to include (overrides exclude) | None |
| `--force-override` | Override existing settings even if already enabled | `False` |
| `--skip-validation` | Skip validation of bucket policies after applying | `False` |

## IAM Permissions Required

The following IAM permissions are required to run this tool:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetAccountPublicAccessBlock",
                "s3:PutAccountPublicAccessBlock"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation",
                "s3:GetBucketPublicAccessBlock",
                "s3:PutBucketPublicAccessBlock",
                "s3:GetBucketPolicy",
                "s3:GetBucketAcl"
            ],
            "Resource": [
                "arn:aws:s3:::*",
                "arn:aws:s3:::*/*"
            ]
        }
    ]
}
```

## Block Public Access Settings

### Account-Level Settings
Applied to the entire AWS account, affecting all buckets:

- **BlockPublicAcls**: Blocks public access granted through new Access Control Lists (ACLs)
- **IgnorePublicAcls**: Ignores public access granted through existing ACLs
- **BlockPublicPolicy**: Blocks public access granted through new bucket policies
- **RestrictPublicBuckets**: Restricts public access granted through bucket policies with public principals

### Bucket-Level Settings
Applied to individual S3 buckets with the same four settings:

- **BlockPublicAcls**: Prevents new public ACLs on the bucket
- **IgnorePublicAcls**: Ignores existing public ACLs on the bucket
- **BlockPublicPolicy**: Prevents new public bucket policies
- **RestrictPublicBuckets**: Restricts public access even with public principals in policies

## Output Examples

### Dry-run Output
```
═══════════════════════════════════════════════════════════════════════════════
                        🛡️  S3 BLOCK PUBLIC ACCESS ENFORCER 🛡️                        
                         Prevent accidental S3 data exposure                    
═══════════════════════════════════════════════════════════════════════════════

[DRY-RUN MODE] S3 Block Public Access Configuration Preview

📊 ACCOUNT-LEVEL ANALYSIS:
┌─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐
│ BlockPublicAcls     │ IgnorePublicAcls    │ BlockPublicPolicy   │ RestrictPublicBuckets│
├─────────────────────┼─────────────────────┼─────────────────────┼─────────────────────┤
│ ❌ False (would set) │ ❌ False (would set) │ ❌ False (would set) │ ❌ False (would set) │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘

📊 BUCKET-LEVEL ANALYSIS:
┌─────────────────────────┬─────────────────┬────────────────┬──────────────────────────┐
│ Bucket Name             │ Region          │ Current Status │ Planned Action           │
├─────────────────────────┼─────────────────┼────────────────┼──────────────────────────┤
│ my-website-bucket       │ us-east-1       │ ❌ Not Protected│ ✅ Enable all settings   │
│ data-backup-bucket      │ us-west-2       │ ⚠️  Partial     │ ✅ Complete protection   │
│ logs-archive-bucket     │ eu-west-1       │ ✅ Protected    │ ➖ No change needed      │
│ public-cdn-assets       │ us-east-1       │ ❌ Not Protected│ ⚠️  EXCLUDED by policy   │
└─────────────────────────┴─────────────────┴────────────────┴──────────────────────────┘

🔧 PLANNED ACTIONS:
  ✅ Enable account-level Block Public Access (all 4 settings)
  ✅ Configure 2 buckets with full Block Public Access
  ✅ Update 1 bucket to complete partial protection
  ⚠️  1 bucket excluded from enforcement (public-cdn-assets)

⚠️  IMPORTANT WARNINGS:
  • Existing public bucket policies may be affected
  • Existing public ACLs will be ignored (not removed)
  • Website hosting buckets may need policy updates
  • CDN/CloudFront distributions may need configuration changes

💰 COST IMPACT:
  • No additional charges for Block Public Access settings
  • Existing data transfer charges remain unchanged

🔄 Run with --apply to implement these changes
```

### Apply Output
```
═══════════════════════════════════════════════════════════════════════════════
                        🛡️  S3 BLOCK PUBLIC ACCESS ENFORCER 🛡️                        
                         Prevent accidental S3 data exposure                    
═══════════════════════════════════════════════════════════════════════════════

✅ S3 Block Public Access Configuration Complete

📊 ACCOUNT-LEVEL RESULTS:
┌─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐
│ BlockPublicAcls     │ IgnorePublicAcls    │ BlockPublicPolicy   │ RestrictPublicBuckets│
├─────────────────────┼─────────────────────┼─────────────────────┼─────────────────────┤
│ ✅ True             │ ✅ True             │ ✅ True             │ ✅ True             │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘

📊 BUCKET-LEVEL RESULTS:
┌─────────────────────────┬─────────────────┬────────────────┬──────────────────────────┐
│ Bucket Name             │ Region          │ Final Status   │ Action Taken             │
├─────────────────────────┼─────────────────┼────────────────┼──────────────────────────┤
│ my-website-bucket       │ us-east-1       │ ✅ Protected    │ ✅ Enabled all settings  │
│ data-backup-bucket      │ us-west-2       │ ✅ Protected    │ ✅ Completed protection  │
│ logs-archive-bucket     │ eu-west-1       │ ✅ Protected    │ ➖ Already configured    │
│ public-cdn-assets       │ us-east-1       │ ❌ Not Protected│ ⚠️  Excluded by policy   │
└─────────────────────────┴─────────────────┴────────────────┴──────────────────────────┘

🔧 ACTIONS COMPLETED:
  ✅ Account-level Block Public Access enabled (all 4 settings)
  ✅ 2 buckets newly protected
  ✅ 1 bucket updated to complete protection
  ✅ 1 bucket excluded as requested

📈 SECURITY IMPROVEMENTS:
  • 100% of in-scope buckets now protected
  • Account-wide protection prevents new public buckets
  • Existing public ACLs are now ignored
  • New bucket policies cannot grant public access

📈 NEXT STEPS:
  • Review excluded buckets for security implications
  • Monitor CloudTrail for any access denied errors
  • Update application code if public access was required
  • Consider using CloudFront for public content delivery
```

### Status Output
```
═══════════════════════════════════════════════════════════════════════════════
                      🛡️  S3 BLOCK PUBLIC ACCESS STATUS REPORT 🛡️                      
                             Current protection posture                         
═══════════════════════════════════════════════════════════════════════════════

📊 ACCOUNT-LEVEL STATUS:
┌─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐
│ BlockPublicAcls     │ IgnorePublicAcls    │ BlockPublicPolicy   │ RestrictPublicBuckets│
├─────────────────────┼─────────────────────┼─────────────────────┼─────────────────────┤
│ ✅ True             │ ✅ True             │ ✅ True             │ ✅ True             │
└─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘

📊 BUCKET PROTECTION SUMMARY:
┌─────────────────┬──────────────┬──────────────┬──────────────┬──────────────────┐
│ Region          │ Total Buckets│ Protected    │ Partial      │ Unprotected      │
├─────────────────┼──────────────┼──────────────┼──────────────┼──────────────────┤
│ us-east-1       │ 12           │ 10           │ 1            │ 1                │
│ us-west-2       │ 8            │ 7            │ 0            │ 1                │
│ eu-west-1       │ 5            │ 5            │ 0            │ 0                │
│ ap-southeast-1  │ 3            │ 3            │ 0            │ 0                │
└─────────────────┴──────────────┴──────────────┴──────────────┴──────────────────┘

🔍 DETAILED BUCKET ANALYSIS:
┌─────────────────────────┬─────────────────┬─────────────┬─────────────┬─────────────┬─────────────────┐
│ Bucket Name             │ Region          │ Block ACLs  │ Ignore ACLs │ Block Policy│ Restrict Buckets│
├─────────────────────────┼─────────────────┼─────────────┼─────────────┼─────────────┼─────────────────┤
│ my-secure-bucket        │ us-east-1       │ ✅ True      │ ✅ True      │ ✅ True      │ ✅ True          │
│ data-backup-bucket      │ us-west-2       │ ✅ True      │ ✅ True      │ ✅ True      │ ✅ True          │
│ partial-protection      │ us-east-1       │ ✅ True      │ ❌ False     │ ✅ True      │ ✅ True          │
│ public-website-bucket   │ us-east-1       │ ❌ False     │ ❌ False     │ ❌ False     │ ❌ False         │
│ unprotected-bucket      │ us-west-2       │ ❌ False     │ ❌ False     │ ❌ False     │ ❌ False         │
└─────────────────────────┴─────────────────┴─────────────┴─────────────┴─────────────┴─────────────────┘

🛡️  PROTECTION EFFECTIVENESS:
  • Overall Protection Rate: 89.3% (25/28 buckets fully protected)
  • Account-level Protection: ✅ Fully Enabled
  • High-risk Buckets: 2 buckets without any protection
  • Partial Protection: 1 bucket needs completion

⚠️  SECURITY RECOMMENDATIONS:
  • Enable full protection for "partial-protection" bucket
  • Review business justification for unprotected buckets
  • Consider CloudFront for public website content
  • Implement bucket policies for granular access control
  • Regular audit of bucket permissions and access patterns
```

## Common Use Cases

### Website Hosting Buckets
```bash
# Exclude website buckets from enforcement
awssec s3-bpa enforce --exclude-buckets my-website-bucket,static-site-bucket --apply

# Use CloudFront instead of direct S3 public access
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json
```

### CDN Assets Buckets
```bash
# Exclude CDN asset buckets but secure with bucket policies
awssec s3-bpa enforce --exclude-buckets cdn-assets-bucket --apply

# Apply restrictive bucket policy
aws s3api put-bucket-policy --bucket cdn-assets-bucket --policy file://cdn-bucket-policy.json
```

### Data Lake Buckets
```bash
# Protect all data lake buckets
awssec s3-bpa enforce --include-buckets data-lake-raw,data-lake-processed,data-lake-curated --apply

# Additional encryption for sensitive data
aws s3api put-bucket-encryption --bucket data-lake-raw --server-side-encryption-configuration file://encryption-config.json
```

## Troubleshooting

### Common Issues

**1. Bucket Policy Conflicts**
```
Error: Cannot enable Block Public Access due to existing bucket policy
```
**Solution**: Review and update bucket policies to remove public access grants.

```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket my-bucket

# Remove conflicting policy statements
aws s3api put-bucket-policy --bucket my-bucket --policy file://updated-policy.json
```

**2. CloudFront Distribution Issues**
```
Warning: Enabling Block Public Access may affect CloudFront distributions
```
**Solution**: Update CloudFront Origin Access Identity (OAI) or Origin Access Control (OAC).

```bash
# Create Origin Access Control
aws cloudfront create-origin-access-control --origin-access-control-config file://oac-config.json

# Update distribution to use OAC
aws cloudfront update-distribution --id DISTRIBUTION_ID --distribution-config file://distribution-config.json
```

**3. Application Access Errors**
```
Error: Access denied after enabling Block Public Access
```
**Solution**: Update application to use IAM roles or signed URLs instead of public access.

```python
# Use IAM roles for EC2 applications
import boto3
s3 = boto3.client('s3')
response = s3.get_object(Bucket='my-bucket', Key='my-file.txt')

# Generate signed URLs for temporary access
url = s3.generate_presigned_url('get_object', 
                               Params={'Bucket': 'my-bucket', 'Key': 'my-file.txt'},
                               ExpiresIn=3600)
```

### Validation Commands

```bash
# Check account-level settings
aws s3api get-public-access-block

# Check bucket-level settings
aws s3api get-bucket-public-access-block --bucket my-bucket

# List all buckets with public access
aws s3api list-buckets --query 'Buckets[?contains(Name, `public`) == `true`]'
```

## Integration Examples

### With CloudTrail
```bash
# Monitor Block Public Access changes
aws logs filter-log-events \
    --log-group-name CloudTrail/S3DataEvents \
    --filter-pattern "{ $.eventName = PutPublicAccessBlock || $.eventName = DeletePublicAccessBlock }"
```

### With Config Rules
```bash
# Monitor compliance with Config Rules
aws configservice put-config-rule --config-rule file://s3-bucket-public-access-prohibited-rule.json

# Check compliance status
aws configservice get-compliance-details-by-config-rule --config-rule-name s3-bucket-public-access-prohibited
```

### With Security Hub
```bash
# S3 findings appear in Security Hub automatically
awssec s3-bpa enforce --apply
awssec securityhub enable --apply

# View S3-related findings
aws securityhub get-findings --filters '{"ResourceType":[{"Value":"AwsS3Bucket","Comparison":"EQUALS"}]}'
```

## Automation Examples

### Lambda Function for New Buckets
```python
import boto3
import json

def lambda_handler(event, context):
    """Automatically apply Block Public Access to new S3 buckets"""
    
    s3 = boto3.client('s3')
    
    # Parse CloudTrail event for S3 bucket creation
    for record in event['Records']:
        if record['eventName'] == 'CreateBucket':
            bucket_name = record['requestParameters']['bucketName']
            
            # Apply Block Public Access settings
            s3.put_bucket_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            
            print(f"Applied Block Public Access to new bucket: {bucket_name}")
    
    return {'statusCode': 200}
```

### Organizations Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Principal": "*",
      "Action": [
        "s3:DeletePublicAccessBlock",
        "s3:PutPublicAccessBlock"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:PrincipalIsAWSService": "false"
        },
        "StringNotEquals": {
          "aws:PrincipalArn": [
            "arn:aws:iam::*:role/SecurityAdminRole",
            "arn:aws:iam::*:role/S3AdminRole"
          ]
        }
      }
    }
  ]
}
```

### Scheduled Compliance Check
```bash
#!/bin/bash
# Scheduled script to ensure S3 Block Public Access compliance

# Run compliance check
awssec s3-bpa status --output json > /tmp/s3-bpa-status.json

# Parse results and send alerts for non-compliant buckets
python3 << EOF
import json
import boto3

with open('/tmp/s3-bpa-status.json') as f:
    status = json.load(f)

unprotected_buckets = [
    bucket for bucket in status['buckets'] 
    if not bucket['fully_protected']
]

if unprotected_buckets:
    sns = boto3.client('sns')
    sns.publish(
        TopicArn='arn:aws:sns:us-east-1:123456789012:security-alerts',
        Subject='S3 Block Public Access Compliance Alert',
        Message=f'Found {len(unprotected_buckets)} unprotected S3 buckets'
    )
EOF
```

## Best Practices

### Gradual Rollout
```bash
# Start with account-level protection
awssec s3-bpa enforce --account-level-only --apply

# Test applications and identify issues
# Then apply bucket-level protection in phases

# Protect non-production buckets first
awssec s3-bpa enforce --include-buckets dev-bucket,test-bucket --apply

# Finally protect production buckets
awssec s3-bpa enforce --exclude-buckets public-website-bucket --apply
```

### Exception Management
```bash
# Maintain list of approved public buckets
APPROVED_PUBLIC_BUCKETS=(
    "company-website-bucket"
    "public-downloads-bucket"
    "cdn-assets-bucket"
)

# Enforce with exceptions
awssec s3-bpa enforce --exclude-buckets $(IFS=,; echo "${APPROVED_PUBLIC_BUCKETS[*]}") --apply
```

## Related Tools

- **CloudTrail**: Logs S3 API calls and Block Public Access changes
- **Config**: Monitors S3 bucket configuration compliance
- **Security Hub**: Aggregates S3 security findings and compliance status
- **IAM Access Analyzer**: Identifies S3 buckets accessible from outside your account