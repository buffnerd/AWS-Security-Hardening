# IAM MFA Enforcement Tool

Reports on and enforces Multi-Factor Authentication (MFA) requirements for IAM users to strengthen account security and prevent unauthorized access.

## Overview

Multi-Factor Authentication (MFA) is a critical security control that adds an extra layer of protection beyond passwords. This tool automates MFA compliance reporting, identifies non-compliant users, and can optionally disable access keys for users without MFA to enforce security policies.

## Features

- **MFA compliance reporting**: Generates comprehensive reports on MFA adoption across IAM users
- **Access key management**: Can disable access keys for users without MFA
- **Console access tracking**: Identifies users with console access but no MFA
- **Policy enforcement**: Applies IAM policies to require MFA for AWS operations
- **Grace period support**: Allows configurable grace periods for new users
- **Bulk operations**: Handles large numbers of IAM users efficiently
- **Multiple output formats**: Table, JSON, and CSV reporting formats

## Usage

### Unified CLI

```bash
# Generate MFA compliance report
awssec iam-mfa report

# Report with dry-run for enforcement actions
awssec iam-mfa enforce --dry-run

# Enforce MFA by disabling non-compliant access keys
awssec iam-mfa enforce --apply

# Report in JSON format
awssec iam-mfa report --output json

# Exclude service accounts from enforcement
awssec iam-mfa enforce --exclude-users svc-backup,svc-monitoring --apply
```

### Standalone Script

```bash
# Generate MFA report
python scripts/iam_mfa_enforce.py --report

# Enforce MFA compliance
python scripts/iam_mfa_enforce.py --enforce --apply

# Dry-run enforcement
python scripts/iam_mfa_enforce.py --enforce --dry-run

# Report with specific output format
python scripts/iam_mfa_enforce.py --report --output csv
```

### Python API

```python
from awssec.tools.iam_mfa import generate_mfa_report, enforce_mfa_compliance

# Generate MFA compliance report
report = generate_mfa_report(
    output_format='json',
    exclude_users=['svc-backup', 'svc-monitoring']
)

# Enforce MFA compliance
results = enforce_mfa_compliance(
    dry_run=False,
    grace_period_days=30,
    exclude_users=['svc-backup']
)
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--report` | Generate MFA compliance report | `False` |
| `--enforce` | Enforce MFA compliance by disabling access keys | `False` |
| `--apply` | Apply changes (required with --enforce unless --dry-run) | `False` |
| `--dry-run` | Show what would be done without making changes | `False` |
| `--exclude-users USERS` | Comma-separated list of users to exclude | None |
| `--include-users USERS` | Comma-separated list of users to include (overrides exclude) | None |
| `--grace-period-days DAYS` | Grace period for new users (days) | `7` |
| `--disable-console-access` | Also disable console access for non-compliant users | `False` |
| `--output FORMAT` | Output format (table/json/csv) | `table` |
| `--save-report PATH` | Save report to file | None |

## IAM Permissions Required

The following IAM permissions are required to run this tool:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:ListUsers",
                "iam:GetUser",
                "iam:ListMFADevices",
                "iam:ListAccessKeys",
                "iam:GetAccessKeyLastUsed",
                "iam:GetLoginProfile"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:UpdateAccessKey",
                "iam:DeleteLoginProfile",
                "iam:AttachUserPolicy",
                "iam:DetachUserPolicy",
                "iam:ListAttachedUserPolicies"
            ],
            "Resource": "arn:aws:iam::*:user/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreatePolicy",
                "iam:GetPolicy",
                "iam:GetPolicyVersion",
                "iam:ListPolicyVersions"
            ],
            "Resource": "arn:aws:iam::*:policy/RequireMFA*"
        }
    ]
}
```

## MFA Compliance Checks

### User Assessment Criteria
The tool evaluates each IAM user based on:

1. **MFA Device Status**: Whether a virtual or hardware MFA device is attached
2. **Console Access**: Whether the user has a login profile for AWS console access
3. **Access Keys**: Whether the user has active access keys
4. **Last Activity**: When the user last accessed AWS services
5. **Account Age**: How long the user account has existed (for grace period)

### Compliance Categories
- **Compliant**: User has MFA enabled and follows security best practices
- **Non-compliant**: User lacks MFA but has console or programmatic access
- **At Risk**: User has console access or active access keys without MFA
- **Exempted**: User explicitly excluded from MFA requirements (service accounts)
- **Grace Period**: New user within the configured grace period

## Output Examples

### Report Output
```
═══════════════════════════════════════════════════════════════════════════════
                             🛡️  IAM MFA COMPLIANCE REPORT 🛡️                             
                          Multi-Factor Authentication Status                     
═══════════════════════════════════════════════════════════════════════════════

📊 MFA COMPLIANCE SUMMARY:
┌─────────────────────┬─────────────┬─────────────────┬─────────────────────────┐
│ Status              │ Count       │ Percentage      │ Risk Level              │
├─────────────────────┼─────────────┼─────────────────┼─────────────────────────┤
│ ✅ Compliant         │ 45          │ 75.0%           │ 🟢 Low                  │
│ ❌ Non-compliant     │ 12          │ 20.0%           │ 🔴 High                 │
│ ⏳ Grace period      │ 2           │ 3.3%            │ 🟡 Medium               │
│ 🚫 Exempted          │ 1           │ 1.7%            │ 🟢 Low (Service Account)│
└─────────────────────┴─────────────┴─────────────────┴─────────────────────────┘

🔍 DETAILED USER ANALYSIS:
┌─────────────────────┬─────────────┬─────────────────┬─────────────┬─────────────────┬─────────────────┐
│ Username            │ MFA Status  │ Console Access  │ Access Keys │ Last Activity   │ Risk Assessment │
├─────────────────────┼─────────────┼─────────────────┼─────────────┼─────────────────┼─────────────────┤
│ john.doe            │ ✅ Enabled   │ ✅ Yes          │ 2 Active    │ 2024-01-15      │ 🟢 Compliant    │
│ jane.smith          │ ✅ Enabled   │ ✅ Yes          │ 1 Active    │ 2024-01-14      │ 🟢 Compliant    │
│ bob.wilson          │ ❌ None      │ ✅ Yes          │ 0 Keys      │ 2024-01-10      │ 🔴 High Risk    │
│ alice.brown         │ ❌ None      │ ❌ No           │ 1 Active    │ 2024-01-12      │ 🔴 High Risk    │
│ new.user            │ ❌ None      │ ✅ Yes          │ 0 Keys      │ Never           │ 🟡 Grace Period │
│ svc-backup          │ ❌ None      │ ❌ No           │ 1 Active    │ 2024-01-15      │ 🟢 Exempted     │
└─────────────────────┴─────────────┴─────────────────┴─────────────┴─────────────────┴─────────────────┘

🚨 HIGH-RISK USERS (Console Access + No MFA):
  • bob.wilson: Console access without MFA protection
  • Priority: Immediate action required

🔑 ACCESS KEY RISKS (Active Keys + No MFA):
  • alice.brown: 1 active access key without MFA
  • Priority: Disable or require MFA immediately

📈 COMPLIANCE TRENDS:
  • Overall compliance: 75.0% (Target: 95%+)
  • Console users with MFA: 70.0% (Target: 100%)
  • Users with active keys + MFA: 85.0% (Target: 100%)

🎯 RECOMMENDATIONS:
  • Focus on console users without MFA (2 users)
  • Implement MFA requirement policy for all operations
  • Consider access key rotation for non-MFA users
  • Set up automated MFA enforcement
```

### Enforcement Dry-run Output
```
═══════════════════════════════════════════════════════════════════════════════
                           🛡️  IAM MFA ENFORCEMENT PREVIEW 🛡️                           
                         Planned compliance enforcement actions                  
═══════════════════════════════════════════════════════════════════════════════

[DRY-RUN MODE] MFA Enforcement Action Preview

📊 ENFORCEMENT TARGETS:
┌─────────────────────┬─────────────────┬─────────────────┬─────────────────────────────────────┐
│ Username            │ Current Status  │ Planned Action  │ Justification                       │
├─────────────────────┼─────────────────┼─────────────────┼─────────────────────────────────────┤
│ bob.wilson          │ Console Only    │ Disable Console │ Console access without MFA          │
│ alice.brown         │ Keys Only       │ Disable Keys    │ Active access key without MFA       │
│ old.account         │ Keys + Console  │ Disable Both    │ Multiple access methods without MFA │
│ new.user            │ Console Only    │ No Action       │ Within 7-day grace period           │
│ svc-backup          │ Keys Only       │ No Action       │ Exempted service account            │
└─────────────────────┴─────────────────┴─────────────────┴─────────────────────────────────────┘

🔧 PLANNED ENFORCEMENT ACTIONS:
  ✅ Disable console access for 2 users
  ✅ Disable access keys for 2 users (3 total keys)
  ✅ Apply MFA-required policy to 3 users
  ⚠️  2 users exempted (service accounts + grace period)

📧 NOTIFICATION PLAN:
  • Send email warnings 24 hours before enforcement
  • Provide MFA setup instructions and deadlines
  • Include links to MFA device setup documentation

⚠️  IMPACT ASSESSMENT:
  • 3 users will lose AWS access until MFA is configured
  • Applications using affected access keys will fail
  • Users have been warned via previous compliance reports

💼 BUSINESS CONTINUITY:
  • Service accounts excluded from enforcement
  • Emergency access procedures documented
  • IT support available for MFA setup assistance

🔄 Run with --apply to implement these enforcement actions
```

### Enforcement Apply Output
```
═══════════════════════════════════════════════════════════════════════════════
                             🛡️  IAM MFA ENFORCEMENT COMPLETE 🛡️                             
                            Compliance enforcement actions taken                
═══════════════════════════════════════════════════════════════════════════════

✅ MFA Enforcement Actions Completed

📊 ENFORCEMENT RESULTS:
┌─────────────────────┬─────────────────┬─────────────────┬─────────────────────────────────────┐
│ Username            │ Previous Status │ Action Taken    │ Current Status                      │
├─────────────────────┼─────────────────┼─────────────────┼─────────────────────────────────────┤
│ bob.wilson          │ Console Only    │ ✅ Console Disabled│ No AWS access                    │
│ alice.brown         │ Keys Only       │ ✅ Keys Disabled   │ No AWS access                    │
│ old.account         │ Keys + Console  │ ✅ Both Disabled   │ No AWS access                    │
│ new.user            │ Console Only    │ ➖ No Action       │ Grace period (5 days remaining) │
│ svc-backup          │ Keys Only       │ ➖ No Action       │ Exempted service account        │
└─────────────────────┴─────────────────┴─────────────────┴─────────────────────────────────────┘

🔧 ACTIONS COMPLETED:
  ✅ Console access disabled for 2 users
  ✅ Access keys disabled for 2 users (3 total keys affected)
  ✅ MFA-required policy attached to 3 users
  ✅ Enforcement notifications sent to affected users

📧 NOTIFICATIONS SENT:
  • Email notifications to all affected users
  • Instructions for MFA device setup included
  • Deadline for compliance: 2024-01-22 (7 days)
  • Support contact information provided

📈 COMPLIANCE IMPROVEMENT:
  • Risk reduction: 3 high-risk users now secured
  • Access keys secured: 3 keys without MFA protection
  • Console access secured: 2 console users without MFA
  • Overall security posture significantly improved

📈 NEXT STEPS:
  • Monitor for MFA device registration by affected users
  • Re-enable access once MFA is properly configured
  • Schedule follow-up compliance report in 7 days
  • Review and update exemption list as needed
```

## MFA Enforcement Policies

### Conditional Access Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "RequireMFAForAllActions",
            "Effect": "Deny",
            "Principal": "*",
            "Action": "*",
            "Resource": "*",
            "Condition": {
                "BoolIfExists": {
                    "aws:MultiFactorAuthPresent": "false"
                },
                "NumericLessThan": {
                    "aws:MultiFactorAuthAge": "3600"
                }
            }
        },
        {
            "Sid": "AllowMFADeviceManagement",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "iam:CreateVirtualMFADevice",
                "iam:EnableMFADevice",
                "iam:ResyncMFADevice",
                "iam:ListMFADevices",
                "iam:GetUser"
            ],
            "Resource": "*"
        }
    ]
}
```

### Self-Service MFA Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowUserToManageOwnMFA",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "iam:CreateVirtualMFADevice",
                "iam:EnableMFADevice",
                "iam:ResyncMFADevice",
                "iam:DeactivateMFADevice",
                "iam:DeleteVirtualMFADevice"
            ],
            "Resource": [
                "arn:aws:iam::*:mfa/${aws:username}",
                "arn:aws:iam::*:user/${aws:username}"
            ]
        },
        {
            "Sid": "AllowUserToListOwnMFA",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "iam:ListMFADevices",
                "iam:ListVirtualMFADevices"
            ],
            "Resource": "*"
        }
    ]
}
```

## Integration Examples

### With AWS SSO
```bash
# For organizations using AWS SSO, focus on break-glass accounts
awssec iam-mfa report --include-users admin-break-glass,emergency-access

# Enforce MFA on local IAM users only
awssec iam-mfa enforce --exclude-users sso-* --apply
```

### With CloudTrail Monitoring
```python
# Lambda function to monitor MFA usage
import boto3
import json

def lambda_handler(event, context):
    """Monitor and alert on non-MFA API calls"""
    
    for record in event['Records']:
        message = json.loads(record['Sns']['Message'])
        
        # Check if API call was made without MFA
        if not message.get('responseElements', {}).get('multiFactorAuthPresent'):
            user_name = message.get('userIdentity', {}).get('userName')
            source_ip = message.get('sourceIPAddress')
            
            # Send alert
            sns = boto3.client('sns')
            sns.publish(
                TopicArn='arn:aws:sns:us-east-1:123456789012:security-alerts',
                Subject=f'Non-MFA API Call Alert',
                Message=f'User {user_name} made API call from {source_ip} without MFA'
            )
    
    return {'statusCode': 200}
```

### With AWS Config
```bash
# Create Config rule to monitor MFA compliance
aws configservice put-config-rule --config-rule file://mfa-enabled-for-iam-console-access.json

# Check compliance status
aws configservice get-compliance-details-by-config-rule --config-rule-name mfa-enabled-for-iam-console-access
```

## Automated Workflows

### New User MFA Setup
```python
# Lambda function for new user MFA setup workflow
import boto3
import json

def lambda_handler(event, context):
    """Automated MFA setup workflow for new users"""
    
    iam = boto3.client('iam')
    ses = boto3.client('ses')
    
    # Detect new user creation
    if event['source'] == 'aws.iam' and event['detail']['eventName'] == 'CreateUser':
        username = event['detail']['requestParameters']['userName']
        
        # Attach MFA requirement policy
        iam.attach_user_policy(
            UserName=username,
            PolicyArn='arn:aws:iam::123456789012:policy/RequireMFAPolicy'
        )
        
        # Send setup instructions
        ses.send_email(
            Source='security@company.com',
            Destination={'ToAddresses': [f'{username}@company.com']},
            Message={
                'Subject': {'Data': 'AWS Account Setup - MFA Required'},
                'Body': {
                    'Text': {
                        'Data': f'''
                        Welcome to AWS, {username}!
                        
                        Before you can access AWS services, you must set up Multi-Factor Authentication (MFA).
                        
                        Setup Instructions:
                        1. Sign in to the AWS Console
                        2. Go to IAM > Users > {username}
                        3. Click "Security credentials" tab
                        4. Click "Manage" next to "Assigned MFA device"
                        5. Follow the setup wizard
                        
                        You have 7 days to complete MFA setup before access is restricted.
                        
                        If you need assistance, contact the IT security team.
                        '''
                    }
                }
            }
        )
        
        print(f"MFA setup workflow initiated for user: {username}")
    
    return {'statusCode': 200}
```

### Scheduled Compliance Enforcement
```bash
#!/bin/bash
# Scheduled script for MFA compliance enforcement

# Generate current compliance report
awssec iam-mfa report --output json > /tmp/mfa-report.json

# Extract non-compliant users outside grace period
NON_COMPLIANT=$(python3 -c "
import json
with open('/tmp/mfa-report.json') as f:
    report = json.load(f)
users = [u['username'] for u in report['users'] if u['status'] == 'non-compliant' and u['days_since_creation'] > 7]
print(','.join(users))
")

if [ -n "$NON_COMPLIANT" ]; then
    echo "Enforcing MFA compliance for users: $NON_COMPLIANT"
    
    # Send warning email first
    python3 send_mfa_warning.py --users "$NON_COMPLIANT"
    
    # Wait 24 hours, then enforce
    echo "Enforcement will proceed in 24 hours"
    # Schedule enforcement with at/cron
    echo "awssec iam-mfa enforce --include-users $NON_COMPLIANT --apply" | at now + 24 hours
else
    echo "All users are MFA compliant"
fi
```

## Troubleshooting

### Common Issues

**1. Service Account False Positives**
```
Issue: Service accounts flagged as non-compliant
```
**Solution**: Use exclude patterns or explicit exemption lists.

```bash
# Exclude service accounts by naming pattern
awssec iam-mfa enforce --exclude-users svc-*,service-*,automation-* --apply

# Use explicit exemption list
awssec iam-mfa enforce --exclude-users svc-backup,svc-monitoring,automation-deploy --apply
```

**2. Cross-Account Access Issues**
```
Error: Cannot disable access keys due to cross-account policies
```
**Solution**: Review and update cross-account trust policies.

```bash
# Check trust policies for the user
aws iam list-attached-user-policies --user-name problem-user
aws iam get-user-policy --user-name problem-user --policy-name inline-policy
```

**3. Emergency Access Scenarios**
```
Issue: Need to restore access for locked-out administrator
```
**Solution**: Use root account or emergency access procedures.

```bash
# Re-enable access key using root account
aws iam update-access-key --user-name locked-admin --access-key-id AKIA... --status Active

# Remove MFA requirement temporarily
aws iam detach-user-policy --user-name locked-admin --policy-arn arn:aws:iam::123456789012:policy/RequireMFAPolicy
```

### Validation Commands

```bash
# Check specific user MFA status
aws iam list-mfa-devices --user-name john.doe

# Check user's attached policies
aws iam list-attached-user-policies --user-name john.doe

# Check access key status
aws iam list-access-keys --user-name john.doe
```

## Best Practices

### Phased Rollout
```bash
# Phase 1: Report and educate
awssec iam-mfa report --save-report mfa-baseline.csv

# Phase 2: Start with development accounts
awssec iam-mfa enforce --include-users dev-* --apply

# Phase 3: Production accounts with longer grace period
awssec iam-mfa enforce --grace-period-days 14 --exclude-users svc-* --apply
```

### Exception Management
```bash
# Document service account exemptions
cat > service-accounts.txt << EOF
svc-backup        # Automated backup service
svc-monitoring    # CloudWatch agent service account
automation-deploy # CI/CD deployment account
EOF

# Apply enforcement with documented exemptions
EXEMPTED_USERS=$(cat service-accounts.txt | grep -v '^#' | awk '{print $1}' | tr '\n' ',' | sed 's/,$//')
awssec iam-mfa enforce --exclude-users "$EXEMPTED_USERS" --apply
```

## Related Tools

- **CloudTrail**: Logs MFA usage and non-MFA API calls for monitoring
- **Config**: Provides MFA compliance rules and continuous monitoring
- **Security Hub**: Aggregates MFA-related security findings
- **AWS SSO**: Provides centralized MFA for federated access