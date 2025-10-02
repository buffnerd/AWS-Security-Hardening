# Least Privilege IAM Policies

This document contains ready-to-use IAM policy JSON snippets for implementing least privilege access.

## Security Toolkit Execution Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "GuardDutyManagement",
            "Effect": "Allow",
            "Action": [
                "guardduty:ListDetectors",
                "guardduty:CreateDetector",
                "guardduty:GetDetector",
                "guardduty:UpdateDetector"
            ],
            "Resource": "*"
        },
        {
            "Sid": "SecurityHubManagement",
            "Effect": "Allow",
            "Action": [
                "securityhub:DescribeHub",
                "securityhub:EnableSecurityHub",
                "securityhub:GetEnabledStandards",
                "securityhub:BatchEnableStandards"
            ],
            "Resource": "*"
        },
        {
            "Sid": "S3PublicAccessManagement",
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketPublicAccessBlock",
                "s3:PutBucketPublicAccessBlock",
                "s3:GetAccountPublicAccessBlock",
                "s3:PutAccountPublicAccessBlock",
                "s3:ListAllMyBuckets"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAMUserManagement",
            "Effect": "Allow",
            "Action": [
                "iam:ListUsers",
                "iam:GetUser",
                "iam:ListMFADevices",
                "iam:ListAccessKeys",
                "iam:UpdateAccessKey",
                "iam:DeleteAccessKey"
            ],
            "Resource": "*"
        },
        {
            "Sid": "EC2SecurityGroupManagement",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeRegions",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupIngress"
            ],
            "Resource": "*"
        },
        {
            "Sid": "CloudTrailManagement",
            "Effect": "Allow",
            "Action": [
                "cloudtrail:DescribeTrails",
                "cloudtrail:CreateTrail",
                "cloudtrail:StartLogging",
                "cloudtrail:PutEventSelectors"
            ],
            "Resource": "*"
        },
        {
            "Sid": "RegionDiscovery",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeRegions",
                "account:GetAlternateContact",
                "account:ListRegions"
            ],
            "Resource": "*"
        }
    ]
}
```

## Read-Only Audit Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "ReadOnlySecurityAudit",
            "Effect": "Allow",
            "Action": [
                "guardduty:List*",
                "guardduty:Get*",
                "guardduty:Describe*",
                "securityhub:List*",
                "securityhub:Get*",
                "securityhub:Describe*",
                "s3:GetBucket*",
                "s3:GetAccount*",
                "s3:ListAllMyBuckets",
                "iam:List*",
                "iam:Get*",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeRegions",
                "cloudtrail:Describe*",
                "cloudtrail:Get*",
                "cloudtrail:List*"
            ],
            "Resource": "*"
        }
    ]
}
```

## Lambda Execution Role Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "guardduty:*",
                "securityhub:*",
                "s3:GetBucket*",
                "s3:PutBucket*",
                "s3:GetAccount*",
                "s3:PutAccount*",
                "s3:ListAllMyBuckets",
                "iam:ListUsers",
                "iam:GetUser",
                "iam:ListMFADevices",
                "iam:ListAccessKeys",
                "iam:UpdateAccessKey",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeRegions",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:RevokeSecurityGroupIngress",
                "cloudtrail:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## Cross-Account Role Template

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::SECURITY-ACCOUNT-ID:root"
            },
            "Action": "sts:AssumeRole",
            "Condition": {
                "StringEquals": {
                    "sts:ExternalId": "unique-external-id"
                }
            }
        }
    ]
}
```