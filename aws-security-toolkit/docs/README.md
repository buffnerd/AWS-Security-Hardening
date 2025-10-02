# AWS Security Toolkit Documentation

Welcome to the AWS Security Toolkit documentation. This toolkit provides comprehensive security hardening capabilities for AWS environments.

## Quick Links

- [Hardening Runbook](hardening-runbook.md) - Safe order of operations and rollback procedures
- [Least Privilege IAM](least-priv-iam.md) - Ready-to-use IAM policies
- [Multi-Account Organization](org-multi-account.md) - Delegated admin patterns
- [Security Group Remediation](sg-remediation-notes.md) - Caveats and recovery steps

## Overview

The AWS Security Toolkit consists of:

1. **Core Modules** - Reusable utilities for regions, logging, CLI, and AWS operations
2. **Security Scripts** - Modular hardening functions for specific AWS services
3. **Executable Entrypoints** - Command-line tools for direct execution
4. **Lambda Handlers** - Serverless deployment options
5. **Infrastructure as Code** - CloudFormation templates for automated deployment

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Configure AWS credentials
3. Review the [hardening runbook](hardening-runbook.md) for safe execution order
4. Run individual scripts or deploy as Lambda functions

## Security Services Covered

- **GuardDuty** - Threat detection enablement
- **Security Hub** - Central security dashboard
- **S3** - Block public access enforcement
- **IAM** - MFA enforcement and access key management
- **EC2** - Security group audit and remediation
- **CloudTrail** - Logging and monitoring setup