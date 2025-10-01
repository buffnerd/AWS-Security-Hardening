# AWS Security Hardening Toolbox

A comprehensive collection of Python scripts for AWS security hardening and compliance. This repository serves as a toolbox for security professionals working on AWS security projects.

## 🎯 Purpose

This repository provides organized, ready-to-use Python scripts for:
- Automating AWS security hardening tasks
- Implementing security best practices
- Compliance checking and remediation
- Security monitoring and alerting
- Incident response automation

## 📁 Repository Structure

```
AWS-Security-Hardening/
├── scripts/              # Category-organized security scripts
│   ├── guardduty/       # Amazon GuardDuty automation
│   ├── iam/             # IAM security and compliance
│   ├── s3/              # S3 bucket security
│   ├── vpc/             # VPC and network security
│   ├── cloudtrail/      # CloudTrail logging
│   ├── config/          # AWS Config rules
│   ├── securityhub/     # Security Hub automation
│   ├── kms/             # Key Management Service
│   ├── ec2/             # EC2 security hardening
│   └── lambda/          # Lambda security
├── utils/               # Shared utility functions
├── docs/                # Documentation and guides
├── examples/            # Example usage and workflows
└── requirements.txt     # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- AWS CLI configured with appropriate credentials
- Required IAM permissions for the scripts you intend to run

### Installation

1. Clone the repository:
```bash
git clone https://github.com/buffnerd/AWS-Security-Hardening.git
cd AWS-Security-Hardening
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials:
```bash
aws configure
```

## 📚 Script Categories

### GuardDuty
Scripts for enabling and managing Amazon GuardDuty across regions and accounts.
- Enable GuardDuty in all regions
- Configure data sources (S3, EBS, Kubernetes)
- Manage findings and alerts

### IAM
Identity and Access Management security automation.
- Password policy enforcement
- MFA compliance checking
- Access key rotation
- Role and policy auditing

### S3
S3 bucket security hardening scripts.
- Bucket encryption enforcement
- Public access blocking
- Versioning and logging configuration
- Bucket policy auditing

### VPC
Virtual Private Cloud security configuration.
- Security group auditing
- Network ACL management
- Flow logs enablement
- VPC endpoint configuration

### CloudTrail
CloudTrail logging and monitoring.
- Multi-region trail setup
- Log file validation
- S3 bucket configuration
- CloudWatch integration

### Config
AWS Config rule management.
- Compliance rule deployment
- Remediation automation
- Configuration snapshots

### Security Hub
Security Hub centralization and management.
- Multi-account setup
- Standards enablement
- Finding aggregation

### KMS
Key Management Service automation.
- Key rotation policies
- Key policy auditing
- Encryption at rest enforcement

### EC2
EC2 instance security hardening.
- Security group compliance
- AMI encryption
- Instance metadata protection
- Systems Manager integration

### Lambda
Lambda function security.
- VPC configuration
- IAM role auditing
- Environment variable encryption

## 🛠️ Usage

Each script is designed to be standalone and includes its own documentation. General usage pattern:

```bash
python scripts/<category>/<script_name>.py [options]
```

For detailed usage of individual scripts, refer to the documentation in each script or the `docs/` directory.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Scripts follow the existing organizational structure
- Code includes proper error handling
- Documentation is updated
- Scripts are tested in a safe environment

## ⚠️ Security Notice

- Always test scripts in a non-production environment first
- Review and understand scripts before execution
- Ensure you have appropriate IAM permissions
- Follow the principle of least privilege
- Never commit AWS credentials to the repository

## 📄 License

This project is intended for security hardening and compliance purposes. Use responsibly and in accordance with AWS policies and your organization's security requirements.

## 🔗 Resources

- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)
- [AWS Well-Architected Framework - Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services)
