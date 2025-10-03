# Security Hub Tool

Enables AWS Security Hub across all regions to centralize security findings and compliance monitoring from multiple AWS security services.

## Overview

AWS Security Hub is a comprehensive security management service that provides a centralized dashboard for security alerts and findings from multiple AWS security services, partner tools, and custom security tools. This tool automates Security Hub deployment with industry-standard compliance frameworks.

## Features

- **Multi-region deployment**: Enables Security Hub across all AWS regions
- **Compliance standards**: Automatically enables AWS Foundational Security Standard and CIS benchmarks
- **Finding aggregation**: Centralizes findings from GuardDuty, Inspector, Macie, and other services
- **Custom insights**: Creates custom insights for security monitoring
- **Multi-account support**: Supports AWS Organizations for centralized security management
- **Automated remediation**: Integrates with AWS Config Rules and Systems Manager for automated response
- **Partner integrations**: Supports third-party security tool integrations

## Usage

### Unified CLI

```bash
# Enable Security Hub with dry-run
awssec securityhub enable --dry-run

# Enable Security Hub with changes applied
awssec securityhub enable --apply

# Check Security Hub status
awssec securityhub status

# Enable in specific regions only
awssec securityhub enable --regions us-east-1,us-west-2 --apply

# Enable specific standards
awssec securityhub enable --aws-foundational --cis-benchmark --apply
```

### Standalone Script

```bash
# Enable Security Hub
python scripts/securityhub_enable.py --apply

# Dry-run mode
python scripts/securityhub_enable.py --dry-run

# Check status only
python scripts/securityhub_enable.py --status-only

# Enable with specific standards
python scripts/securityhub_enable.py --aws-foundational --cis-benchmark --pci-dss --apply
```

### Python API

```python
from awssec.tools.securityhub import enable_securityhub, check_securityhub_status

# Enable Security Hub with standards
results = enable_securityhub(
    regions=['us-east-1', 'us-west-2'],
    dry_run=False,
    enable_aws_foundational=True,
    enable_cis_benchmark=True,
    enable_pci_dss=False
)

# Check status across all regions
status = check_securityhub_status()
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--apply` | Apply changes (required unless --dry-run) | `False` |
| `--dry-run` | Show what would be done without making changes | `False` |
| `--status-only` | Only check current Security Hub status | `False` |
| `--regions REGIONS` | Comma-separated list of regions | All regions |
| `--aws-foundational` | Enable AWS Foundational Security Standard | `True` |
| `--cis-benchmark` | Enable CIS AWS Foundations Benchmark | `True` |
| `--pci-dss` | Enable PCI DSS v3.2.1 | `False` |
| `--nist-800-53` | Enable NIST 800-53 Rev. 5 | `False` |
| `--enable-default-standards` | Enable all default standards | `True` |
| `--finding-format` | Finding format (ASFF/JSON) | `ASFF` |

## IAM Permissions Required

The following IAM permissions are required to run this tool:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "securityhub:EnableSecurityHub",
                "securityhub:GetEnabledStandards",
                "securityhub:BatchEnableStandards",
                "securityhub:BatchDisableStandards",
                "securityhub:DescribeHub",
                "securityhub:UpdateSecurityHubConfiguration"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "securityhub:CreateMembers",
                "securityhub:InviteMembers",
                "securityhub:AcceptInvitation",
                "securityhub:DisassociateMembers",
                "securityhub:DeleteMembers",
                "securityhub:GetMembers"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "securityhub:CreateInsight",
                "securityhub:UpdateInsight",
                "securityhub:GetInsights",
                "securityhub:GetFindings"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "config:DescribeConfigurationRecorders",
                "config:DescribeDeliveryChannels",
                "config:GetComplianceDetailsByConfigRule",
                "config:GetComplianceSummaryByConfigRule"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateServiceLinkedRole"
            ],
            "Resource": "arn:aws:iam::*:role/aws-service-role/securityhub.amazonaws.com/AWSServiceRoleForSecurityHub"
        }
    ]
}
```

## Compliance Standards

### AWS Foundational Security Standard
Comprehensive set of security controls covering:
- **IAM**: Password policies, MFA requirements, access key rotation
- **EC2**: Security group configurations, EBS encryption, AMI security
- **S3**: Bucket policies, encryption, public access blocks
- **RDS**: Encryption, backup configurations, security groups
- **Lambda**: Function permissions, VPC configurations
- **CloudTrail**: Logging configurations, log file validation

### CIS AWS Foundations Benchmark
Industry-standard security configurations:
- **Identity and Access Management**: 1.1-1.22
- **Logging**: 2.1-2.9
- **Monitoring**: 3.1-3.15
- **Networking**: 4.1-4.4

### PCI DSS v3.2.1
Payment card industry security requirements:
- **Network security**: Firewalls, network segmentation
- **Data protection**: Encryption, access controls
- **Vulnerability management**: Regular scanning, patching
- **Access control**: Multi-factor authentication, least privilege

### NIST 800-53 Rev. 5
Federal security standards for:
- **Access Control**: Account management, authentication
- **Audit and Accountability**: Event logging, monitoring
- **Configuration Management**: Baseline configurations
- **Incident Response**: Response procedures, communications

## Output Examples

### Dry-run Output
```
═══════════════════════════════════════════════════════════════════════════════
                           🛡️  SECURITY HUB ENABLER 🛡️                           
                      Centralized security findings management                   
═══════════════════════════════════════════════════════════════════════════════

[DRY-RUN MODE] Security Hub Configuration Preview

📊 ANALYSIS RESULTS:
┌─────────────────┬──────────────┬──────────────┬─────────────┬──────────────────┐
│ Region          │ Status       │ AWS Found.   │ CIS Bench.  │ Standards Count  │
├─────────────────┼──────────────┼──────────────┼─────────────┼──────────────────┤
│ us-east-1       │ ❌ Disabled   │ N/A          │ N/A         │ 0                │
│ us-west-2       │ ✅ Enabled    │ ✅ Enabled    │ ❌ Disabled  │ 1                │
│ eu-west-1       │ ❌ Disabled   │ N/A          │ N/A         │ 0                │
│ ap-southeast-1  │ ❌ Disabled   │ N/A          │ N/A         │ 0                │
└─────────────────┴──────────────┴──────────────┴─────────────┴──────────────────┘

🔧 PLANNED ACTIONS:
  ✅ Enable Security Hub in 3 regions
  ✅ Subscribe to AWS Foundational Security Standard in 4 regions
  ✅ Subscribe to CIS AWS Foundations Benchmark in 4 regions
  ✅ Configure default finding aggregation region (us-east-1)
  ✅ Create service-linked role for Security Hub

📋 STANDARDS TO BE ENABLED:
  • AWS Foundational Security Standard v1.0.0
  • CIS AWS Foundations Benchmark v1.2.0

💰 ESTIMATED COSTS:
  • Security Hub: $0.0010 per finding ingested
  • Standards subscriptions: No additional charge
  • Config Rules: $0.003 per rule evaluation (for standards)

🔄 Run with --apply to implement these changes
```

### Apply Output
```
═══════════════════════════════════════════════════════════════════════════════
                           🛡️  SECURITY HUB ENABLER 🛡️                           
                      Centralized security findings management                   
═══════════════════════════════════════════════════════════════════════════════

✅ Security Hub Configuration Complete

📊 RESULTS SUMMARY:
┌─────────────────┬──────────────┬──────────────┬─────────────┬──────────────────┐
│ Region          │ Status       │ AWS Found.   │ CIS Bench.  │ Standards Count  │
├─────────────────┼──────────────┼──────────────┼─────────────┼──────────────────┤
│ us-east-1       │ ✅ Enabled    │ ✅ Enabled    │ ✅ Enabled   │ 2                │
│ us-west-2       │ ✅ Enabled    │ ✅ Enabled    │ ✅ Enabled   │ 2                │
│ eu-west-1       │ ✅ Enabled    │ ✅ Enabled    │ ✅ Enabled   │ 2                │
│ ap-southeast-1  │ ✅ Enabled    │ ✅ Enabled    │ ✅ Enabled   │ 2                │
└─────────────────┴──────────────┴──────────────┴─────────────┴──────────────────┘

🔧 ACTIONS COMPLETED:
  ✅ Security Hub enabled in 4 regions
  ✅ AWS Foundational Security Standard subscribed (4 regions)
  ✅ CIS AWS Foundations Benchmark subscribed (4 regions)
  ✅ Service-linked role created
  ✅ Finding aggregation configured

📈 NEXT STEPS:
  • Configure custom insights for your environment
  • Set up automated remediation with AWS Config Rules
  • Enable additional security services (GuardDuty, Inspector)
  • Configure SNS notifications for critical findings
  • Review and customize finding filters
```

### Status Output
```
═══════════════════════════════════════════════════════════════════════════════
                         🛡️  SECURITY HUB STATUS REPORT 🛡️                         
                            Current compliance posture                          
═══════════════════════════════════════════════════════════════════════════════

📊 SECURITY HUB STATUS ACROSS REGIONS:
┌─────────────────┬──────────────┬──────────────┬─────────────┬──────────────────┐
│ Region          │ Hub Status   │ AWS Found.   │ CIS Bench.  │ Finding Sources  │
├─────────────────┼──────────────┼──────────────┼─────────────┼──────────────────┤
│ us-east-1       │ ✅ Active     │ ✅ Enabled    │ ✅ Enabled   │ 5                │
│ us-west-2       │ ✅ Active     │ ✅ Enabled    │ ✅ Enabled   │ 3                │
│ eu-west-1       │ ✅ Active     │ ✅ Enabled    │ ❌ Disabled  │ 2                │
│ ap-southeast-1  │ ❌ Disabled   │ N/A          │ N/A         │ 0                │
└─────────────────┴──────────────┴──────────────┴─────────────┴──────────────────┘

📈 COMPLIANCE SUMMARY (Last 7 days):
┌─────────────────┬──────────────┬──────────────┬──────────────┬─────────────────┐
│ Standard        │ Passed       │ Failed       │ Not Available│ Compliance Score│
├─────────────────┼──────────────┼──────────────┼──────────────┼─────────────────┤
│ AWS Foundational│ 45           │ 12           │ 3            │ 78.9%           │
│ CIS Benchmark   │ 28           │ 8            │ 2            │ 77.8%           │
└─────────────────┴──────────────┴──────────────┴──────────────┴─────────────────┘

🔍 TOP FAILING CONTROLS:
┌─────────────────────────────────────────────────────────────┬──────────────┐
│ Control                                                     │ Failed Count │
├─────────────────────────────────────────────────────────────┼──────────────┤
│ [EC2.2] VPC default security groups should not allow...    │ 8            │
│ [IAM.3] Users' access keys should be rotated every 90...   │ 6            │
│ [S3.1] S3 Block Public Access setting should be enabled   │ 4            │
│ [CloudTrail.1] CloudTrail should be enabled and configured │ 3            │
└─────────────────────────────────────────────────────────────┴──────────────┘

🔍 RECENT FINDINGS BY SEVERITY:
┌─────────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Region          │ Critical     │ High         │ Medium       │ Low          │
├─────────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ us-east-1       │ 2            │ 8            │ 15           │ 23           │
│ us-west-2       │ 0            │ 3            │ 12           │ 18           │
│ eu-west-1       │ 1            │ 5            │ 9            │ 14           │
└─────────────────┴──────────────┴──────────────┴──────────────┴──────────────┘

🎯 RECOMMENDATIONS:
  • Enable Security Hub in ap-southeast-1
  • Enable CIS Benchmark in eu-west-1
  • Address critical findings in us-east-1 and eu-west-1
  • Configure automated remediation for common failures
```

## Integration with Security Services

### GuardDuty Integration
```bash
# Enable both services together
awssec guardduty enable --apply
awssec securityhub enable --apply

# GuardDuty findings automatically appear in Security Hub
```

### Config Integration
```bash
# Security Hub leverages Config for compliance checks
aws configservice put-configuration-recorder --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/aws-config-role
aws configservice put-delivery-channel --delivery-channel name=default,s3BucketName=config-bucket-123456789012

# Enable Security Hub (will use Config rules)
awssec securityhub enable --apply
```

### Inspector Integration
```bash
# Enable Inspector for vulnerability assessments
aws inspector2 enable --account-ids 123456789012 --resource-types ECR,EC2

# Findings automatically flow to Security Hub
```

## Automated Remediation

### AWS Config Rules Integration
```python
# Lambda function for automated remediation
import boto3

def lambda_handler(event, context):
    securityhub = boto3.client('securityhub')
    
    # Parse Security Hub finding
    finding = event['detail']['findings'][0]
    compliance_status = finding['Compliance']['Status']
    
    if compliance_status == 'FAILED':
        resource_type = finding['Resources'][0]['Type']
        
        if resource_type == 'AwsS3Bucket':
            # Remediate S3 bucket public access
            remediate_s3_public_access(finding)
        elif resource_type == 'AwsEc2SecurityGroup':
            # Remediate security group rules
            remediate_security_group(finding)
    
    return {'statusCode': 200}

def remediate_s3_public_access(finding):
    s3 = boto3.client('s3')
    bucket_name = finding['Resources'][0]['Id'].split('/')[-1]
    
    s3.put_bucket_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': True,
            'IgnorePublicAcls': True,
            'BlockPublicPolicy': True,
            'RestrictPublicBuckets': True
        }
    )
```

### Systems Manager Integration
```bash
# Create Systems Manager document for remediation
aws ssm create-document \
    --content file://remediation-document.json \
    --name "SecurityHub-S3-RemediatePublicAccess" \
    --document-type "Automation"

# Configure Security Hub to trigger remediation
aws securityhub update-finding \
    --finding-identifiers file://finding-ids.json \
    --note "Automated remediation triggered"
```

## Custom Insights

### Creating Custom Insights
```python
import boto3

def create_custom_insights():
    securityhub = boto3.client('securityhub')
    
    # Insight for critical findings
    securityhub.create_insight(
        Name='Critical Security Findings',
        Filters={
            'SeverityLabel': [{'Value': 'CRITICAL', 'Comparison': 'EQUALS'}],
            'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
        },
        GroupByAttribute='ResourceType'
    )
    
    # Insight for compliance violations
    securityhub.create_insight(
        Name='Compliance Violations by Resource',
        Filters={
            'ComplianceStatus': [{'Value': 'FAILED', 'Comparison': 'EQUALS'}],
            'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
        },
        GroupByAttribute='ResourceType'
    )
```

## Multi-Account Management

### Organizations Setup
```bash
# Enable Security Hub in master account
awssec securityhub enable --apply

# Invite member accounts
aws securityhub create-members \
    --account-details file://member-accounts.json

# Accept invitations in member accounts
aws securityhub accept-invitation \
    --master-id 123456789012 \
    --invitation-id <invitation-id>
```

### Cross-Region Finding Aggregation
```bash
# Configure aggregation region
aws securityhub create-finding-aggregator \
    --region-linking-mode ALL_REGIONS
```

## Troubleshooting

### Common Issues

**1. Config Required for Standards**
```
Error: AWS Config must be enabled for compliance standards
```
**Solution**: Enable AWS Config before enabling Security Hub standards.

**2. Service-Linked Role Creation**
```
Error: Cannot create service-linked role
```
**Solution**: Ensure IAM permissions for creating service-linked roles.

**3. Finding Format Issues**
```
Error: Invalid finding format specified
```
**Solution**: Use ASFF (AWS Security Finding Format) for best compatibility.

**4. Standards Subscription Limits**
```
Error: Maximum number of standards subscriptions reached
```
**Solution**: Review and disable unused standards before enabling new ones.

### Validation Commands

```bash
# Check Security Hub status
aws securityhub describe-hub --region us-east-1

# List enabled standards
aws securityhub get-enabled-standards --region us-east-1

# Get compliance summary
aws securityhub get-findings --filters '{"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}' --region us-east-1
```

## Cost Optimization

### Region Selection
```bash
# Enable in primary regions only
awssec securityhub enable --regions us-east-1,us-west-2 --apply

# Use finding aggregation for centralized visibility
aws securityhub create-finding-aggregator --region us-east-1
```

### Standards Management
```bash
# Enable only required standards
awssec securityhub enable --aws-foundational --apply

# Disable unused standards
aws securityhub batch-disable-standards \
    --standards-subscription-arns arn:aws:securityhub:us-east-1:123456789012:subscription/cis-aws-foundations-benchmark/v/1.2.0
```

## Related Tools

- **GuardDuty**: Threat detection findings integrate with Security Hub
- **Config**: Provides configuration compliance data for Security Hub standards
- **Inspector**: Vulnerability assessment findings appear in Security Hub
- **CloudTrail**: API logs support Security Hub compliance checks
- **Systems Manager**: Enables automated remediation of Security Hub findings