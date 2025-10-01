# GuardDuty Scripts

Scripts for managing and automating Amazon GuardDuty configuration and operations.

## Available Scripts

### enable_guardduty.py

Enable Amazon GuardDuty across all enabled regions in your AWS account.

**Features:**
- Enables GuardDuty in all enabled regions
- Configures S3 Protection for S3 bucket monitoring
- Enables EBS Malware Protection for EC2 instance scanning
- Enables Kubernetes Protection for EKS cluster monitoring
- Supports dry-run mode for testing
- Multi-region support

**Usage:**
```bash
# Enable GuardDuty in all enabled regions
python enable_guardduty.py

# Enable with specific AWS profile
python enable_guardduty.py --profile production

# Dry-run mode (show what would be done)
python enable_guardduty.py --dry-run

# Enable in specific regions only
python enable_guardduty.py --regions us-east-1,us-west-2

# Enable with debug logging
python enable_guardduty.py --log-level DEBUG
```

**Required IAM Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "guardduty:CreateDetector",
        "guardduty:ListDetectors",
        "guardduty:UpdateDetector",
        "guardduty:UpdateMalwareProtectionPlan",
        "ec2:DescribeRegions"
      ],
      "Resource": "*"
    }
  ]
}
```

## Future Scripts

Additional GuardDuty scripts planned:
- `disable_guardduty.py` - Safely disable GuardDuty
- `export_findings.py` - Export GuardDuty findings to S3
- `configure_notifications.py` - Setup SNS notifications for findings
- `manage_trusted_ips.py` - Manage trusted IP lists
- `manage_threat_lists.py` - Manage threat intelligence feeds
