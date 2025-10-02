# Multi-Account Organization Patterns

This document outlines patterns for implementing the AWS Security Toolkit across multi-account AWS Organizations.

## Architecture Overview

### Centralized Security Account Pattern

```
┌─────────────────────────────────────────────────────┐
│                Security Account                      │
│  ┌─────────────────────────────────────────────────┤
│  │ AWS Security Toolkit                            │
│  │ - Lambda Functions                              │
│  │ - EventBridge Schedulers                       │
│  │ - Cross-Account IAM Roles                      │
│  └─────────────────────────────────────────────────┤
└─────────────────────────────────────────────────────┘
                         │
                         │ Assume Role
                         ▼
┌─────────────────────────────────────────────────────┐
│               Member Accounts                       │
│  ┌─────────────────────────────────────────────────┤
│  │ Target Resources                               │
│  │ - GuardDuty Detectors                         │
│  │ - Security Hub                                │
│  │ - S3 Buckets                                  │
│  │ - IAM Users                                   │
│  │ - Security Groups                             │
│  │ - CloudTrail                                  │
│  └─────────────────────────────────────────────────┤
└─────────────────────────────────────────────────────┘
```

## Implementation Steps

### 1. Deploy Delegated Administrator

```bash
# In Organization management account
aws organizations enable-aws-service-access --service-principal guardduty.amazonaws.com
aws organizations enable-aws-service-access --service-principal securityhub.amazonaws.com

# Register delegated administrator
aws organizations register-delegated-administrator \
    --account-id SECURITY-ACCOUNT-ID \
    --service-principal guardduty.amazonaws.com

aws organizations register-delegated-administrator \
    --account-id SECURITY-ACCOUNT-ID \
    --service-principal securityhub.amazonaws.com
```

### 2. Create Cross-Account Execution Role

Deploy this role in each member account:

```yaml
# cross-account-security-role.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Cross-account role for AWS Security Toolkit'

Parameters:
  SecurityAccountId:
    Type: String
    Description: 'Account ID of the central security account'

Resources:
  SecurityToolkitExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: 'SecurityToolkitExecutionRole'
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              AWS: !Sub 'arn:aws:iam::${SecurityAccountId}:root'
            Action: sts:AssumeRole
            Condition:
              StringEquals:
                'sts:ExternalId': 'security-toolkit-2024'
      ManagedPolicyArns:
        - 'arn:aws:iam::aws:policy/SecurityAudit'
      Policies:
        - PolicyName: 'SecurityToolkitPermissions'
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - 'guardduty:*'
                  - 'securityhub:*'
                  - 's3:PutBucketPublicAccessBlock'
                  - 's3:PutAccountPublicAccessBlock'
                  - 'iam:UpdateAccessKey'
                  - 'iam:DeleteAccessKey'
                  - 'ec2:AuthorizeSecurityGroupIngress'
                  - 'ec2:RevokeSecurityGroupIngress'
                  - 'cloudtrail:*'
                Resource: '*'

Outputs:
  RoleArn:
    Description: 'ARN of the cross-account execution role'
    Value: !GetAtt SecurityToolkitExecutionRole.Arn
```

### 3. Deploy Security Toolkit in Central Account

```bash
# Deploy the toolkit Lambda functions
cd infra/lambda
./build.sh

# Deploy CloudFormation schedulers
aws cloudformation deploy \
    --template-file ../cfn/scheduler-guardduty.yaml \
    --stack-name security-toolkit-guardduty \
    --capabilities CAPABILITY_IAM
```

### 4. Configure Organization-Wide Settings

```python
# Example: Configure toolkit for organization
import boto3

def get_organization_accounts():
    """Get all accounts in the organization."""
    org_client = boto3.client('organizations')
    accounts = []
    
    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        accounts.extend(page['Accounts'])
    
    return [acc for acc in accounts if acc['Status'] == 'ACTIVE']

def assume_cross_account_role(account_id, role_name):
    """Assume role in target account."""
    sts_client = boto3.client('sts')
    
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='SecurityToolkitExecution',
        ExternalId='security-toolkit-2024'
    )
    
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken']
    )
```

## Deployment Patterns

### Pattern 1: StackSets Deployment

```yaml
# Deploy cross-account roles using StackSets
aws cloudformation create-stack-set \
    --stack-set-name SecurityToolkitRoles \
    --template-body file://cross-account-security-role.yaml \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameters ParameterKey=SecurityAccountId,ParameterValue=123456789012

# Deploy to all organization accounts
aws cloudformation create-stack-instances \
    --stack-set-name SecurityToolkitRoles \
    --deployment-targets OrganizationalUnitIds=r-xxxx \
    --regions us-east-1 \
    --operation-preferences MaxConcurrentPercentage=100
```

### Pattern 2: Gradual Rollout

1. **Phase 1**: Deploy to sandbox/dev accounts
2. **Phase 2**: Deploy to staging accounts
3. **Phase 3**: Deploy to production accounts

### Pattern 3: Service-Specific Deployment

Deploy individual services across accounts in stages:

1. CloudTrail (logging foundation)
2. GuardDuty (threat detection)
3. Security Hub (centralized findings)
4. IAM hardening
5. Network security

## Monitoring and Reporting

### Organization-Wide Dashboard

```python
def generate_org_security_report():
    """Generate organization-wide security compliance report."""
    accounts = get_organization_accounts()
    report = {
        'guardduty_enabled': {},
        'securityhub_enabled': {},
        'cloudtrail_enabled': {},
        'mfa_compliance': {}
    }
    
    for account in accounts:
        account_id = account['Id']
        session = assume_cross_account_role(account_id, 'SecurityToolkitExecutionRole')
        
        # Check GuardDuty status
        guardduty = session.client('guardduty')
        detectors = guardduty.list_detectors()
        report['guardduty_enabled'][account_id] = len(detectors['DetectorIds']) > 0
        
        # Check Security Hub status
        try:
            securityhub = session.client('securityhub')
            hub = securityhub.describe_hub()
            report['securityhub_enabled'][account_id] = True
        except:
            report['securityhub_enabled'][account_id] = False
    
    return report
```

## Best Practices

1. **Use least privilege IAM policies**
2. **Implement proper error handling and retries**
3. **Monitor cross-account role usage**
4. **Regularly audit permissions**
5. **Use AWS Config for compliance monitoring**
6. **Implement proper logging and alerting**
7. **Test disaster recovery procedures**

## Troubleshooting

### Common Issues

1. **Cross-account role assumption failures**
   - Check trust policy
   - Verify external ID
   - Ensure proper permissions

2. **Service enablement failures**
   - Check service quotas
   - Verify regional availability
   - Review conflicting configurations

3. **Organization permissions**
   - Verify delegated administrator setup
   - Check SCP restrictions
   - Review organization settings