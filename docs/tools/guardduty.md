# GuardDuty Security Tool

Enables AWS GuardDuty threat detection service across all regions to monitor for malicious activity and unauthorized behavior.

## Overview

AWS GuardDuty is a threat detection service that continuously monitors your AWS accounts and workloads for malicious activity. This tool automates the deployment and configuration of GuardDuty across all AWS regions with security best practices.

## Features

- **Multi-region deployment**: Enables GuardDuty across all AWS regions simultaneously
- **Threat intelligence**: Leverages AWS threat intelligence feeds and machine learning
- **VPC Flow Logs monitoring**: Analyzes network traffic patterns for anomalies
- **DNS logs analysis**: Monitors DNS queries for malicious domains
- **CloudTrail integration**: Analyzes API calls for suspicious activity
- **S3 protection**: Monitors S3 bucket access patterns and configurations
- **EKS audit logs**: Analyzes Kubernetes API server audit logs
- **Malware detection**: Scans EBS volumes for malware
- **Runtime monitoring**: Monitors EC2 instances and container workloads for threats

## Usage

### Unified CLI

```bash
# Enable GuardDuty with dry-run
awssec guardduty enable --dry-run

# Enable GuardDuty with changes applied
awssec guardduty enable --apply

# Check GuardDuty status
awssec guardduty status

# Enable in specific regions only
awssec guardduty enable --regions us-east-1,us-west-2 --apply

# Enable with specific protection plans
awssec guardduty enable --s3-protection --malware-protection --apply
```

### Standalone Script

```bash
# Enable GuardDuty
python scripts/guardduty_enable.py --apply

# Dry-run mode
python scripts/guardduty_enable.py --dry-run

# Check status only
python scripts/guardduty_enable.py --status-only

# Enable with all protection features
python scripts/guardduty_enable.py --s3-protection --malware-protection --eks-protection --apply
```

### Python API

```python
from awssec.tools.guardduty import enable_guardduty, check_guardduty_status

# Enable GuardDuty with protection features
results = enable_guardduty(
    regions=['us-east-1', 'us-west-2'],
    dry_run=False,
    s3_protection=True,
    malware_protection=True,
    eks_protection=True
)

# Check status across all regions
status = check_guardduty_status()
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--apply` | Apply changes (required unless --dry-run) | `False` |
| `--dry-run` | Show what would be done without making changes | `False` |
| `--status-only` | Only check current GuardDuty status | `False` |
| `--regions REGIONS` | Comma-separated list of regions | All regions |
| `--s3-protection` | Enable S3 protection | `False` |
| `--malware-protection` | Enable EBS malware protection | `False` |
| `--eks-protection` | Enable EKS audit log monitoring | `False` |
| `--runtime-monitoring` | Enable runtime monitoring | `False` |
| `--auto-enable-s3` | Auto-enable S3 protection for new accounts | `False` |
| `--finding-frequency` | Finding publishing frequency | `FIFTEEN_MINUTES` |

## IAM Permissions Required

The following IAM permissions are required to run this tool:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "guardduty:CreateDetector",
                "guardduty:GetDetector",
                "guardduty:UpdateDetector",
                "guardduty:ListDetectors",
                "guardduty:UpdateMemberDetectors",
                "guardduty:CreateMembers",
                "guardduty:GetMembers",
                "guardduty:InviteMembers"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "guardduty:UpdateS3BucketResource",
                "guardduty:UpdateMalwareProtection",
                "guardduty:UpdateEksClusterResource",
                "guardduty:UpdateRuntimeMonitoringResource"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateServiceLinkedRole"
            ],
            "Resource": "arn:aws:iam::*:role/aws-service-role/guardduty.amazonaws.com/AWSServiceRoleForAmazonGuardDuty"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateServiceLinkedRole"
            ],
            "Resource": "arn:aws:iam::*:role/aws-service-role/malware-protection.guardduty.amazonaws.com/AWSServiceRoleForAmazonGuardDutyMalwareProtection"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeImages",
                "ec2:DescribeSnapshots",
                "ec2:DescribeVolumes"
            ],
            "Resource": "*"
        }
    ]
}
```

## Protection Features

### Core Detection
- **VPC Flow Logs**: Monitors network traffic for reconnaissance, instance compromise, and data exfiltration
- **DNS Logs**: Detects communication with malicious domains and DNS tunneling
- **CloudTrail Events**: Identifies suspicious API calls and privilege escalation attempts

### S3 Protection
- **Bucket scanning**: Monitors S3 bucket policies and ACLs for misconfigurations
- **Data access monitoring**: Detects unusual data access patterns
- **Policy analysis**: Identifies overly permissive bucket policies

### Malware Protection
- **EBS volume scanning**: Scans EBS volumes attached to EC2 instances for malware
- **On-demand scanning**: Triggered by GuardDuty findings or manual requests
- **Automatic remediation**: Can automatically isolate infected instances

### EKS Protection
- **Audit log monitoring**: Analyzes Kubernetes API server audit logs
- **Container threat detection**: Identifies malicious container activity
- **Privilege escalation**: Detects unauthorized privilege escalation in clusters

### Runtime Monitoring
- **Process monitoring**: Monitors running processes for malicious activity
- **File system monitoring**: Detects unauthorized file system modifications
- **Network monitoring**: Analyzes runtime network connections

## Output Examples

### Dry-run Output
```
═══════════════════════════════════════════════════════════════════════════════
                             🛡️  GUARDDUTY ENABLER 🛡️                             
                        Threat detection across all regions                      
═══════════════════════════════════════════════════════════════════════════════

[DRY-RUN MODE] GuardDuty Configuration Preview

📊 ANALYSIS RESULTS:
┌─────────────────┬──────────────┬─────────────┬─────────────┬─────────────────┐
│ Region          │ Status       │ S3 Protect  │ Malware     │ EKS Protect     │
├─────────────────┼──────────────┼─────────────┼─────────────┼─────────────────┤
│ us-east-1       │ ❌ Disabled   │ N/A         │ N/A         │ N/A             │
│ us-west-2       │ ✅ Enabled    │ ❌ Disabled  │ ❌ Disabled  │ ❌ Disabled      │
│ eu-west-1       │ ❌ Disabled   │ N/A         │ N/A         │ N/A             │
│ ap-southeast-1  │ ❌ Disabled   │ N/A         │ N/A         │ N/A             │
└─────────────────┴──────────────┴─────────────┴─────────────┴─────────────────┘

🔧 PLANNED ACTIONS:
  ✅ Enable GuardDuty in 3 regions
  ✅ Configure S3 protection in 4 regions
  ✅ Enable malware protection for EBS volumes
  ✅ Set up EKS audit log monitoring
  ✅ Configure finding publication frequency to 15 minutes

⚠️  IMPORTANT NOTES:
  • S3 protection incurs additional charges (~$0.50 per 1M API calls)
  • Malware protection charges apply per GB scanned (~$0.10 per GB)
  • EKS protection requires EKS clusters with audit logging enabled

💰 ESTIMATED COSTS:
  • GuardDuty base: $4.00/month per region
  • VPC Flow Logs: $0.50 per 1M flow log records
  • DNS queries: $0.40 per 1M queries
  • S3 protection: $0.50 per 1M S3 API calls analyzed
  • Malware protection: $0.10 per GB scanned

🔄 Run with --apply to implement these changes
```

### Apply Output
```
═══════════════════════════════════════════════════════════════════════════════
                             🛡️  GUARDDUTY ENABLER 🛡️                             
                        Threat detection across all regions                      
═══════════════════════════════════════════════════════════════════════════════

✅ GuardDuty Configuration Complete

📊 RESULTS SUMMARY:
┌─────────────────┬──────────────┬─────────────┬─────────────┬─────────────────┐
│ Region          │ Status       │ S3 Protect  │ Malware     │ EKS Protect     │
├─────────────────┼──────────────┼─────────────┼─────────────┼─────────────────┤
│ us-east-1       │ ✅ Enabled    │ ✅ Enabled   │ ✅ Enabled   │ ✅ Enabled       │
│ us-west-2       │ ✅ Enabled    │ ✅ Enabled   │ ✅ Enabled   │ ✅ Enabled       │
│ eu-west-1       │ ✅ Enabled    │ ✅ Enabled   │ ✅ Enabled   │ ✅ Enabled       │
│ ap-southeast-1  │ ✅ Enabled    │ ✅ Enabled   │ ✅ Enabled   │ ✅ Enabled       │
└─────────────────┴──────────────┴─────────────┴─────────────┴─────────────────┘

🔧 ACTIONS COMPLETED:
  ✅ GuardDuty enabled in 4 regions
  ✅ S3 protection configured for all regions
  ✅ Malware protection activated
  ✅ EKS audit log monitoring enabled
  ✅ Service-linked roles created automatically

📈 NEXT STEPS:
  • Configure SNS notifications for findings
  • Set up automated remediation with Lambda
  • Review and tune finding suppression rules
  • Enable GuardDuty in AWS Organizations for centralized management
  • Configure threat intelligence feeds
```

### Status Output
```
═══════════════════════════════════════════════════════════════════════════════
                           🛡️  GUARDDUTY STATUS REPORT 🛡️                           
                            Current protection coverage                         
═══════════════════════════════════════════════════════════════════════════════

📊 GUARDDUTY STATUS ACROSS REGIONS:
┌─────────────────┬──────────────┬─────────────┬─────────────┬─────────────┬───────────────┐
│ Region          │ Detector     │ S3 Protect  │ Malware     │ EKS Protect │ Last Updated  │
├─────────────────┼──────────────┼─────────────┼─────────────┼─────────────┼───────────────┤
│ us-east-1       │ ✅ Active     │ ✅ Enabled   │ ✅ Enabled   │ ✅ Enabled   │ 2024-01-15    │
│ us-west-2       │ ✅ Active     │ ✅ Enabled   │ ✅ Enabled   │ ✅ Enabled   │ 2024-01-15    │
│ eu-west-1       │ ✅ Active     │ ❌ Disabled  │ ❌ Disabled  │ ❌ Disabled  │ 2024-01-10    │
│ ap-southeast-1  │ ❌ Disabled   │ N/A         │ N/A         │ N/A         │ N/A           │
└─────────────────┴──────────────┴─────────────┴─────────────┴─────────────┴───────────────┘

📈 RECENT FINDINGS (Last 7 days):
┌─────────────────┬──────────────┬─────────────┬───────────────────────────────┐
│ Region          │ High         │ Medium      │ Most Common Type              │
├─────────────────┼──────────────┼─────────────┼───────────────────────────────┤
│ us-east-1       │ 0            │ 3           │ Recon:EC2/PortProbeIPv4       │
│ us-west-2       │ 1            │ 5           │ UnauthorizedAPICall:IAMUser   │
│ eu-west-1       │ 0            │ 2           │ Stealth:IAMUser/CloudTrailOff │
└─────────────────┴──────────────┴─────────────┴───────────────────────────────┘

🔍 RECOMMENDATIONS:
  • Enable missing protection features in eu-west-1
  • Activate GuardDuty in ap-southeast-1
  • Review and remediate high-severity findings in us-west-2
  • Consider enabling threat intelligence feeds
```

## Troubleshooting

### Common Issues

**1. Service-Linked Role Creation Failed**
```
Error: Access denied when creating service-linked role
```
**Solution**: Ensure the IAM user/role has `iam:CreateServiceLinkedRole` permission.

**2. GuardDuty Already Enabled**
```
Error: DetectorId already exists
```
**Solution**: The tool handles existing detectors and will update configuration.

**3. S3 Protection Costs**
```
Warning: S3 protection will incur additional charges
```
**Solution**: Review S3 protection pricing and use `--dry-run` to estimate costs.

**4. EKS Clusters Not Found**
```
Warning: No EKS clusters found for audit log monitoring
```
**Solution**: EKS protection requires existing EKS clusters with audit logging enabled.

### Validation Commands

```bash
# Check GuardDuty detector status
aws guardduty list-detectors --region us-east-1

# Get detector configuration
aws guardduty get-detector --detector-id <detector-id> --region us-east-1

# List recent findings
aws guardduty list-findings --detector-id <detector-id> --region us-east-1
```

## Integration Examples

### With Security Hub
```bash
# GuardDuty findings automatically appear in Security Hub
awssec guardduty enable --apply
awssec securityhub enable --apply
```

### With AWS Organizations
```bash
# Enable GuardDuty in master account first
awssec guardduty enable --apply

# Then configure as GuardDuty master for organization
aws guardduty create-members --detector-id <detector-id> \
    --account-details AccountId=123456789012,Email=security@company.com
```

### Automated Response
```python
# Lambda function for automated GuardDuty response
import boto3

def lambda_handler(event, context):
    finding = event['detail']
    finding_type = finding['type']
    
    if finding_type.startswith('UnauthorizedAPICall'):
        # Disable compromised access key
        iam = boto3.client('iam')
        username = finding['service']['remoteIpDetails']['organization']['org']
        # Add remediation logic here
    
    return {'statusCode': 200}
```

### SNS Notifications
```bash
# Create SNS topic for GuardDuty findings
aws sns create-topic --name guardduty-findings

# Subscribe email to topic
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:123456789012:guardduty-findings \
    --protocol email --notification-endpoint security@company.com

# Configure GuardDuty to publish to SNS (via CloudWatch Events)
```

## Multi-Account Management

### GuardDuty Master Account Setup
```bash
# Enable GuardDuty in master account
awssec guardduty enable --apply

# Invite member accounts
aws guardduty create-members --detector-id <detector-id> \
    --account-details file://member-accounts.json

# Accept invitations in member accounts
aws guardduty accept-invitation --detector-id <detector-id> \
    --master-id 123456789012 --invitation-id <invitation-id>
```

### Organization-wide Deployment
```bash
#!/bin/bash
# Deploy GuardDuty across AWS Organization

# Master account
awssec guardduty enable --apply

# Member accounts
for ACCOUNT in $(aws organizations list-accounts --query 'Accounts[].Id' --output text); do
    echo "Enabling GuardDuty in account: $ACCOUNT"
    awssec guardduty enable \
        --assume-role-arn "arn:aws:iam::${ACCOUNT}:role/OrganizationAccountAccessRole" \
        --apply
done
```

## Cost Optimization

### Selective Feature Enablement
```bash
# Enable only core features in dev environments
awssec guardduty enable --apply  # Core features only

# Enable all features in production
awssec guardduty enable --s3-protection --malware-protection --eks-protection --apply
```

### Region-Specific Deployment
```bash
# Enable in primary regions only
awssec guardduty enable --regions us-east-1,us-west-2,eu-west-1 --apply

# Add secondary regions later
awssec guardduty enable --regions ap-southeast-1,ap-northeast-1 --apply
```

## Related Tools

- **Security Hub**: Centralizes GuardDuty findings with other security tools
- **CloudTrail**: Provides the API logs that GuardDuty analyzes
- **Config**: Tracks configuration changes that might affect GuardDuty
- **Inspector**: Complements GuardDuty with vulnerability assessments