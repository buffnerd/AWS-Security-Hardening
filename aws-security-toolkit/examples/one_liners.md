# One-Liner Command Examples

This document contains copy-paste examples for common AWS security operations.

## GuardDuty

```bash
# Enable GuardDuty in all regions
python bin/enable_guardduty_all_regions.py

# Check GuardDuty status
aws guardduty list-detectors --region us-east-1
```

## Security Hub

```bash
# Enable Security Hub in all regions
python bin/enable_securityhub_all_regions.py

# Check Security Hub status
aws securityhub describe-hub --region us-east-1
```

## S3 Security

```bash
# Block public access for all S3 buckets
python bin/s3_block_public_access_everywhere.py

# Check S3 bucket public access
aws s3api get-public-access-block --bucket my-bucket
```

## IAM MFA

```bash
# Generate MFA report and disable non-MFA user access keys
python bin/iam_enforce_mfa_report_and_disable_keys.py

# List users without MFA
aws iam list-users --query 'Users[?MfaDevices==`[]`]'
```

## Security Groups

```bash
# Audit and fix open security groups
python bin/ec2_sg_audit_and_fix_open_ports.py

# List security groups with open SSH
aws ec2 describe-security-groups --filters "Name=ip-permission.from-port,Values=22" "Name=ip-permission.cidr,Values=0.0.0.0/0"
```

## CloudTrail

```bash
# Enable CloudTrail in all regions
python bin/cloudtrail_enable_multiregion.py

# Check CloudTrail status
aws cloudtrail describe-trails --region us-east-1
```