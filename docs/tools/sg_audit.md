# Security Group Audit Tool

Audits and fixes risky security group configurations to prevent unauthorized network access and reduce attack surface.

## Overview

Security groups act as virtual firewalls for EC2 instances and other AWS resources. This tool identifies overly permissive security group rules, analyzes network exposure risks, and can automatically remediate common security issues while maintaining operational functionality.

## Features

- **Comprehensive rule analysis**: Examines all inbound and outbound security group rules
- **Risk assessment**: Categorizes rules by risk level (Critical, High, Medium, Low)
- **Automated remediation**: Can automatically fix common security group misconfigurations
- **Usage analysis**: Identifies unused security groups and rules
- **Port scanning detection**: Flags commonly exploited ports and protocols
- **CIDR analysis**: Evaluates IP range permissions and public access
- **Compliance reporting**: Generates detailed security group compliance reports
- **Multi-region support**: Audits security groups across all AWS regions

## Usage

### Unified CLI

```bash
# Audit security groups with detailed report
awssec sg audit

# Audit with dry-run remediation preview
awssec sg audit --fix --dry-run

# Apply automatic fixes for critical issues
awssec sg fix --apply

# Audit specific regions only
awssec sg audit --regions us-east-1,us-west-2

# Focus on specific security groups
awssec sg audit --security-groups sg-12345678,sg-87654321
```

### Standalone Script

```bash
# Audit security groups
python scripts/security_group_audit_fix.py --audit

# Audit and show fix recommendations
python scripts/security_group_audit_fix.py --audit --show-fixes

# Apply fixes with confirmation
python scripts/security_group_audit_fix.py --fix --apply

# Generate JSON report
python scripts/security_group_audit_fix.py --audit --output json
```

### Python API

```python
from awssec.tools.sg_audit import audit_security_groups, fix_security_groups

# Audit security groups
audit_results = audit_security_groups(
    regions=['us-east-1', 'us-west-2'],
    include_unused=True,
    risk_threshold='medium'
)

# Apply fixes for critical issues
fix_results = fix_security_groups(
    dry_run=False,
    fix_critical_only=True,
    exclude_groups=['sg-production-web']
)
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--audit` | Perform security group audit | `True` |
| `--fix` | Apply security group fixes | `False` |
| `--apply` | Apply changes (required with --fix unless --dry-run) | `False` |
| `--dry-run` | Show what would be done without making changes | `False` |
| `--regions REGIONS` | Comma-separated list of regions | All regions |
| `--security-groups SGS` | Comma-separated list of specific security groups | All groups |
| `--exclude-groups SGS` | Comma-separated list of groups to exclude | None |
| `--risk-threshold LEVEL` | Minimum risk level to report (low/medium/high/critical) | `low` |
| `--fix-critical-only` | Only fix critical risk issues | `False` |
| `--include-unused` | Include unused security groups in audit | `True` |
| `--show-usage` | Show security group usage details | `False` |

## IAM Permissions Required

The following IAM permissions are required to run this tool:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSecurityGroupRules",
                "ec2:DescribeInstances",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeVpcs",
                "ec2:DescribeSubnets"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupEgress",
                "ec2:ModifySecurityGroupRules"
            ],
            "Resource": "arn:aws:ec2:*:*:security-group/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "elasticloadbalancing:DescribeLoadBalancers",
                "rds:DescribeDBInstances",
                "redshift:DescribeClusters",
                "elasticache:DescribeCacheClusters"
            ],
            "Resource": "*"
        }
    ]
}
```

## Risk Assessment Criteria

### Critical Risk (🔴)
- **0.0.0.0/0 on sensitive ports**: SSH (22), RDP (3389), database ports
- **Administrative access**: Full internet access to management protocols
- **Database exposure**: Public access to MySQL, PostgreSQL, MongoDB, etc.
- **Unrestricted protocols**: Any protocol allowing 0.0.0.0/0 access

### High Risk (🟠)
- **Wide CIDR ranges**: Large IP ranges (>1000 addresses) on sensitive ports
- **Common attack vectors**: Telnet, FTP, SNMP with broad access
- **Internal exposure**: Private network ranges exposed unnecessarily
- **Unused rules**: Overly permissive rules on unused ports

### Medium Risk (🟡)
- **HTTP/HTTPS exposure**: Web traffic from any source without CloudFront
- **Application ports**: Custom application ports with broad access
- **Development protocols**: Debug or development ports in production
- **Legacy protocols**: Outdated protocols with security vulnerabilities

### Low Risk (🟢)
- **Specific IP access**: Limited IP ranges for legitimate access
- **Standard protocols**: Well-secured standard ports with proper restrictions
- **VPC-only access**: Access limited to VPC CIDR ranges
- **Least privilege**: Minimal necessary access configurations

## Output Examples

### Audit Report
```
═══════════════════════════════════════════════════════════════════════════════
                         🛡️  SECURITY GROUP AUDIT REPORT 🛡️                         
                              Network security assessment                       
═══════════════════════════════════════════════════════════════════════════════

📊 SECURITY GROUP SUMMARY:
┌─────────────────┬─────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ Region          │ Total Groups│ Critical    │ High Risk   │ Medium Risk │ Low Risk    │
├─────────────────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ us-east-1       │ 45          │ 3           │ 8           │ 12          │ 22          │
│ us-west-2       │ 32          │ 1           │ 5           │ 9           │ 17          │
│ eu-west-1       │ 28          │ 2           │ 4           │ 7           │ 15          │
└─────────────────┴─────────────┴─────────────┴─────────────┴─────────────┴─────────────┘

🔴 CRITICAL SECURITY ISSUES:
┌──────────────────────────┬─────────────────┬──────────────┬──────────────────────────────────────┐
│ Security Group           │ Region          │ Risk         │ Issue Description                    │
├──────────────────────────┼─────────────────┼──────────────┼──────────────────────────────────────┤
│ sg-web-open              │ us-east-1       │ 🔴 Critical  │ SSH (22) open to 0.0.0.0/0          │
│ sg-database-public       │ us-east-1       │ 🔴 Critical  │ MySQL (3306) open to 0.0.0.0/0      │
│ sg-admin-wide            │ us-east-1       │ 🔴 Critical  │ RDP (3389) open to 0.0.0.0/0        │
│ sg-legacy-app            │ us-west-2       │ 🔴 Critical  │ All ports (0-65535) open to internet│
│ sg-prod-mgmt             │ eu-west-1       │ 🔴 Critical  │ SSH (22) + RDP (3389) to 0.0.0.0/0  │
│ sg-test-mongodb          │ eu-west-1       │ 🔴 Critical  │ MongoDB (27017) open to 0.0.0.0/0   │
└──────────────────────────┴─────────────────┴──────────────┴──────────────────────────────────────┘

🟠 HIGH-RISK SECURITY ISSUES:
┌──────────────────────────┬─────────────────┬──────────────┬──────────────────────────────────────┐
│ Security Group           │ Region          │ Risk         │ Issue Description                    │
├──────────────────────────┼─────────────────┼──────────────┼──────────────────────────────────────┤
│ sg-app-server            │ us-east-1       │ 🟠 High      │ SSH (22) open to 10.0.0.0/8         │
│ sg-web-cluster           │ us-east-1       │ 🟠 High      │ HTTP (80) without CloudFront         │
│ sg-dev-environment       │ us-west-2       │ 🟠 High      │ Multiple dev ports to broad ranges   │
└──────────────────────────┴─────────────────┴──────────────┴──────────────────────────────────────┘

📋 DETAILED RULE ANALYSIS:
┌──────────────────────────┬──────────────┬─────────────┬──────────────┬─────────────────────────────┐
│ Security Group           │ Direction    │ Protocol    │ Port Range   │ Source/Destination          │
├──────────────────────────┼──────────────┼─────────────┼──────────────┼─────────────────────────────┤
│ sg-web-open              │ Inbound      │ TCP         │ 22           │ 0.0.0.0/0 🔴                │
│ sg-web-open              │ Inbound      │ TCP         │ 80           │ 0.0.0.0/0 🟡                │
│ sg-web-open              │ Inbound      │ TCP         │ 443          │ 0.0.0.0/0 🟡                │
│ sg-database-public       │ Inbound      │ TCP         │ 3306         │ 0.0.0.0/0 🔴                │
│ sg-database-public       │ Inbound      │ TCP         │ 22           │ 10.0.0.0/16 🟢              │
│ sg-admin-wide            │ Inbound      │ TCP         │ 3389         │ 0.0.0.0/0 🔴                │
│ sg-admin-wide            │ Inbound      │ TCP         │ 22           │ 203.0.113.0/24 🟢           │
└──────────────────────────┴──────────────┴─────────────┴──────────────┴─────────────────────────────┘

🔍 USAGE ANALYSIS:
┌──────────────────────────┬─────────────┬─────────────────┬─────────────────────────────────────────┐
│ Security Group           │ Attached To │ Instance Count  │ Usage Status                            │
├──────────────────────────┼─────────────┼─────────────────┼─────────────────────────────────────────┤
│ sg-web-open              │ EC2         │ 5 instances     │ 🟢 Active                               │
│ sg-database-public       │ RDS         │ 2 instances     │ 🟢 Active                               │
│ sg-unused-old            │ None        │ 0 instances     │ 🟡 Unused (candidate for deletion)     │
│ sg-legacy-app            │ ELB         │ 1 load balancer │ 🟠 Active but misconfigured            │
└──────────────────────────┴─────────────┴─────────────────┴─────────────────────────────────────────┘

📈 RISK METRICS:
  • Critical issues requiring immediate attention: 6
  • High-risk configurations: 17
  • Unused security groups: 8
  • Groups with overly broad access: 12
  • Overall security score: 62/100 (Needs Improvement)

🎯 TOP RECOMMENDATIONS:
  1. Remove 0.0.0.0/0 access from SSH and RDP ports
  2. Restrict database access to application security groups only
  3. Implement bastion hosts for administrative access
  4. Use CloudFront for public web traffic
  5. Delete unused security groups
  6. Replace broad IP ranges with specific security group references
```

### Fix Preview (Dry-run)
```
═══════════════════════════════════════════════════════════════════════════════
                       🛡️  SECURITY GROUP FIX PREVIEW 🛡️                       
                          Planned remediation actions                          
═══════════════════════════════════════════════════════════════════════════════

[DRY-RUN MODE] Security Group Remediation Preview

🔧 PLANNED REMEDIATION ACTIONS:

📊 CRITICAL FIXES:
┌──────────────────────────┬─────────────────────────────────────────────────────────────────┐
│ Security Group           │ Planned Action                                                  │
├──────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ sg-web-open              │ ❌ Remove SSH (22) access from 0.0.0.0/0                        │
│                          │ ✅ Add SSH (22) access from sg-bastion-hosts                   │
│ sg-database-public       │ ❌ Remove MySQL (3306) access from 0.0.0.0/0                   │
│                          │ ✅ Add MySQL (3306) access from sg-app-servers                 │
│ sg-admin-wide            │ ❌ Remove RDP (3389) access from 0.0.0.0/0                     │
│                          │ ✅ Add RDP (3389) access from sg-admin-workstations            │
│ sg-legacy-app            │ ❌ Remove all ports (0-65535) access from 0.0.0.0/0            │
│                          │ ✅ Add specific ports: 80, 443, 8080 from sg-load-balancers   │
└──────────────────────────┴─────────────────────────────────────────────────────────────────┘

📊 HIGH-RISK FIXES:
┌──────────────────────────┬─────────────────────────────────────────────────────────────────┐
│ Security Group           │ Planned Action                                                  │
├──────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ sg-app-server            │ ✅ Replace SSH (22) from 10.0.0.0/8 with sg-bastion-hosts     │
│ sg-web-cluster           │ ✅ Add CloudFront prefix list for HTTP/HTTPS access            │
│ sg-dev-environment       │ ⚠️  Consolidate dev ports and restrict to VPC CIDR             │
└──────────────────────────┴─────────────────────────────────────────────────────────────────┘

🧹 CLEANUP ACTIONS:
┌──────────────────────────┬─────────────────────────────────────────────────────────────────┐
│ Security Group           │ Planned Action                                                  │
├──────────────────────────┼─────────────────────────────────────────────────────────────────┤
│ sg-unused-old            │ 🗑️  Delete unused security group (no attachments)              │
│ sg-duplicate-web         │ 🔄 Consolidate with sg-web-primary (identical rules)           │
│ sg-temporary-test        │ 🗑️  Delete test security group (created 90+ days ago)          │
└──────────────────────────┴─────────────────────────────────────────────────────────────────┘

⚠️  IMPACT ANALYSIS:
  • 6 critical security vulnerabilities will be resolved
  • 0 service disruptions expected (using security group references)
  • 3 unused security groups will be removed
  • Network access patterns will remain functional

💼 DEPENDENCY CHECKS:
  ✅ sg-bastion-hosts exists and has proper configuration
  ✅ sg-app-servers exists and is attached to application instances
  ✅ sg-admin-workstations exists with corporate IP ranges
  ✅ sg-load-balancers exists and is attached to ELBs
  ❌ CloudFront prefix list not configured (will create)

🔄 Run with --apply to implement these security improvements
```

### Fix Application Results
```
═══════════════════════════════════════════════════════════════════════════════
                         🛡️  SECURITY GROUP FIXES APPLIED 🛡️                         
                           Network security improvements                        
═══════════════════════════════════════════════════════════════════════════════

✅ Security Group Remediation Complete

📊 REMEDIATION SUMMARY:
┌─────────────────────┬─────────────┬─────────────┬─────────────┬─────────────────┐
│ Fix Category        │ Planned     │ Successful  │ Failed      │ Success Rate    │
├─────────────────────┼─────────────┼─────────────┼─────────────┼─────────────────┤
│ Critical Fixes      │ 6           │ 6           │ 0           │ 100%            │
│ High-Risk Fixes     │ 3           │ 3           │ 0           │ 100%            │
│ Cleanup Actions     │ 3           │ 2           │ 1           │ 67%             │
└─────────────────────┴─────────────┴─────────────┴─────────────┴─────────────────┘

🔧 ACTIONS COMPLETED:

✅ CRITICAL VULNERABILITIES FIXED:
  • sg-web-open: Removed SSH access from internet, added bastion host access
  • sg-database-public: Removed MySQL internet access, restricted to app servers
  • sg-admin-wide: Removed RDP internet access, restricted to admin workstations
  • sg-legacy-app: Removed unrestricted access, added specific port access
  • sg-prod-mgmt: Secured management ports with proper access controls
  • sg-test-mongodb: Removed MongoDB internet access, restricted to dev environment

✅ HIGH-RISK CONFIGURATIONS IMPROVED:
  • sg-app-server: Replaced broad SSH access with bastion host reference
  • sg-web-cluster: Added CloudFront prefix list for web traffic
  • sg-dev-environment: Consolidated development ports and restricted access

✅ CLEANUP COMPLETED:
  • sg-unused-old: Successfully deleted (no dependencies)
  • sg-temporary-test: Successfully deleted (no dependencies)
  • sg-duplicate-web: ⚠️  Could not delete (still has dependencies, marked for review)

📈 SECURITY IMPROVEMENTS:
  • Critical vulnerabilities eliminated: 6
  • High-risk exposures reduced: 3
  • Internet-facing attack surface reduced by 78%
  • Compliance score improved from 62/100 to 91/100

🛡️  COMPLIANCE STATUS:
  • CIS AWS Foundations Benchmark: ✅ Compliant
  • SOC 2 Network Security: ✅ Compliant
  • PCI DSS Network Isolation: ✅ Compliant
  • Internal Security Policy: ✅ Compliant

📈 NEXT STEPS:
  • Monitor network connectivity for any unexpected access issues
  • Review sg-duplicate-web dependencies for consolidation
  • Schedule regular security group audits (recommended: monthly)
  • Consider implementing AWS Config rules for ongoing monitoring
```

## Common Security Issues

### SSH/RDP Exposure
```bash
# Find SSH/RDP exposed to internet
awssec sg audit --risk-threshold critical

# Fix with bastion host approach
awssec sg fix --apply --fix-critical-only
```

### Database Exposure
```bash
# Audit database port exposure
awssec sg audit | grep -E "(3306|5432|1433|27017)"

# Automatically restrict to application security groups
awssec sg fix --apply
```

### Unused Security Groups
```bash
# Identify unused security groups
awssec sg audit --include-unused --show-usage

# Clean up unused groups
awssec sg fix --apply
```

## Automated Remediation

### Common Fix Patterns

**1. Internet SSH/RDP Access**
- Remove 0.0.0.0/0 access from ports 22 and 3389
- Add access from bastion host security group
- Maintain operational connectivity

**2. Database Internet Exposure**
- Remove 0.0.0.0/0 access from database ports
- Add access from application tier security groups
- Preserve application functionality

**3. Overly Broad Internal Access**
- Replace large CIDR ranges with specific security group references
- Maintain least privilege access
- Improve security without breaking functionality

**4. Unused Security Groups**
- Identify groups with no attachments
- Verify no dependencies exist
- Safely remove unused groups

### Custom Remediation Rules
```python
# Custom remediation configuration
REMEDIATION_RULES = {
    'critical_ports': [22, 3389, 1433, 3306, 5432, 27017],
    'allowed_sources': {
        'ssh': ['sg-bastion-hosts'],
        'rdp': ['sg-admin-workstations'],
        'database': ['sg-app-servers', 'sg-web-tier']
    },
    'web_ports': [80, 443],
    'management_ports': [22, 3389, 5986, 5985]
}
```

## Integration Examples

### With AWS Config
```bash
# Create Config rules for security group monitoring
aws configservice put-config-rule --config-rule file://sg-ssh-restricted.json
aws configservice put-config-rule --config-rule file://sg-database-restricted.json

# Monitor compliance
aws configservice get-compliance-summary-by-config-rule
```

### With CloudTrail
```python
# Monitor security group changes
import boto3
import json

def lambda_handler(event, context):
    """Monitor and alert on risky security group changes"""
    
    risky_actions = [
        'AuthorizeSecurityGroupIngress',
        'AuthorizeSecurityGroupEgress',
        'CreateSecurityGroup'
    ]
    
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        
        if message.get('eventName') in risky_actions:
            # Check if rule allows 0.0.0.0/0 access
            ip_ranges = message.get('requestParameters', {}).get('ipRanges', [])
            
            for ip_range in ip_ranges:
                if ip_range.get('cidrIp') == '0.0.0.0/0':
                    # Send alert
                    sns = boto3.client('sns')
                    sns.publish(
                        TopicArn='arn:aws:sns:us-east-1:123456789012:security-alerts',
                        Subject='Risky Security Group Change Detected',
                        Message=f'Internet access granted in security group: {message}'
                    )
    
    return {'statusCode': 200}
```

### With Security Hub
```bash
# Security group findings appear in Security Hub
awssec sg audit
awssec securityhub enable --apply

# View security group findings
aws securityhub get-findings --filters '{"ResourceType":[{"Value":"AwsEc2SecurityGroup","Comparison":"EQUALS"}]}'
```

## Troubleshooting

### Common Issues

**1. Dependencies Preventing Cleanup**
```
Error: Cannot delete security group sg-12345678 because it is referenced by other security groups
```
**Solution**: Find and update references before deletion.

```bash
# Find security groups referencing the target
aws ec2 describe-security-groups --filters "Name=ip-permission.group-id,Values=sg-12345678"

# Update references, then delete
aws ec2 revoke-security-group-ingress --group-id sg-87654321 --source-groups GroupId=sg-12345678
aws ec2 delete-security-group --group-id sg-12345678
```

**2. Network Connectivity Issues After Fixes**
```
Issue: Application cannot connect after security group changes
```
**Solution**: Verify security group references and port configurations.

```bash
# Check current security group rules
aws ec2 describe-security-groups --group-ids sg-12345678

# Test connectivity
telnet target-host 80
nc -zv target-host 443
```

**3. False Positive Risk Assessments**
```
Issue: Legitimate configurations flagged as high risk
```
**Solution**: Use exclusion lists and custom risk thresholds.

```bash
# Exclude specific security groups from audit
awssec sg audit --exclude-groups sg-legacy-system,sg-special-case

# Adjust risk threshold
awssec sg audit --risk-threshold high
```

### Validation Commands

```bash
# Verify security group configuration
aws ec2 describe-security-groups --group-ids sg-12345678

# Check security group usage
aws ec2 describe-instances --filters "Name=instance.group-id,Values=sg-12345678"

# Validate network connectivity
aws ec2 describe-vpc-endpoints --filters "Name=group-id,Values=sg-12345678"
```

## Best Practices

### Regular Auditing
```bash
# Schedule monthly security group audits
0 0 1 * * awssec sg audit --output json > /var/log/aws/sg-audit-$(date +\%Y-\%m).json

# Alert on critical issues
awssec sg audit --risk-threshold critical | grep -q "Critical" && \
    echo "Critical security group issues found" | mail -s "AWS Security Alert" security@company.com
```

### Gradual Remediation
```bash
# Start with critical issues only
awssec sg fix --fix-critical-only --apply

# Progress to high-risk issues
awssec sg fix --risk-threshold high --apply

# Finally address medium and low risk
awssec sg fix --apply
```

### Change Management
```bash
# Always dry-run first
awssec sg fix --dry-run > planned-changes.txt

# Review and approve changes
# Apply in maintenance window
awssec sg fix --apply
```

## Related Tools

- **VPC Flow Logs**: Analyze actual network traffic patterns for security group optimization
- **AWS Config**: Continuous monitoring of security group compliance
- **Security Hub**: Centralized security group findings and compliance reporting
- **CloudTrail**: Audit trail for security group configuration changes
- **Inspector**: Network reachability analysis and vulnerability assessment