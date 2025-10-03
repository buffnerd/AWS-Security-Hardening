# AWS Security Toolkit (Python)

Harden your AWS accounts quickly with concise, idempotent, and well-commented Python scripts. Each tool## Install

### Option 1: Package Installation (Recommended)
```bash
git clone https://github.com/buffnerd/AWS-Security-Hardening.git
cd AWS-Security-Hardening
pip install -e .
```

This installs the `awssec` unified CLI command and all dependencies.

### Option 2: Script-only Installation
```bash
git clone https://github.com/buffnerd/AWS-Security-Hardening.git
cd AWS-Security-Hardening
pip install -r requirements.txt
```

_If `requirements.txt` isn't present, install `boto3` and `botocore` directly._a common security gap (e.g., GuardD### 4. IAM: Report Non-MFA Users (Optional Key Disable)

**File:** `iam_enforce_mfa_report_and_disable_keys.py` | **📖 [Detailed Documentation](docs/tools/iam_mfa.md)**  
Prints `User,HasMFA,ActiveKeys,KeysDisabled` to stdout. With `--apply`, disables active access keys for users without MFA.

**Quick Usage:**
```bash
python iam_enforce_mfa_report_and_disable_keys.py > no-mfa-report.csv
python iam_enforce_mfa_report_and_disable_keys.py --apply
# or via unified CLI: awssec iam-mfa report
```

**Validate:**  
Re-run report; or:
```bash
aws iam list-access-keys --user-name <User>
```
**Recommend:** Pair with a global "deny unless MFA" policy (exempt break-glass roles).ty Hub, S3 public access, CloudTrail, IAM MFA, Security Groups) and can be safely re-run to enforce baseline posture across all enabled regions.

**Built for speed, clarity, and ops:**  
- Dry-run modes where destructive  
- Retries for resilience  
- `--profile` support  
- Copy-pasteable commands

---

## Table of Contents

- [What's Inside](#whats-inside)
- [🚀 Unified CLI Interface](#-unified-cli-interface)
- [📚 Comprehensive Documentation](#-comprehensive-documentation)
- [Design Goals](#design-goals)
- [Prerequisites](#prerequisites)
- [Install](#install)
- [Usage (One-liners)](#usage-one-liners)
- [Scripts Overview](#scripts-overview)
  - [1. GuardDuty Everywhere](#1-guardduty-everywhere)
  - [2. Security Hub Everywhere + Standards](#2-security-hub-everywhere--standards)
  - [3. S3 Block Public Access (Account + Buckets)](#3-s3-block-public-access-account--buckets)
  - [4. IAM: Report Non-MFA Users (Optional Key Disable)](#4-iam-report-non-mfa-users-optional-key-disable)
  - [5. EC2 Security Groups: Audit & Fix Open Ports](#5-ec2-security-groups-audit--fix-open-ports)
  - [6. CloudTrail: Multi-Region With Validation](#6-cloudtrail-multi-region-with-validation)
- [Least-Privilege IAM](#least-privilege-iam)
- [Recommended Run Order](#recommended-run-order)
- [Automation (Lambda + EventBridge)](#automation-lambda--eventbridge)
- [Multi-Account / Organizations](#multi-account--organizations)
- [Safety, Rollback & Notes](#safety-rollback--notes)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License & Disclaimer](#license--disclaimer)

---

## What's Inside

- ✅ **GuardDuty:** Enable everywhere (+ best-effort data sources)
- ✅ **Security Hub:** Enable everywhere + subscribe to FSBP & CIS 1.4
- ✅ **S3:** Enforce Block Public Access at account and bucket level
- ✅ **IAM:** Report users without MFA (optional: disable active access keys)
- ✅ **Security Groups:** Audit & fix risky rules (wide-open sensitive ports)
- ✅ **CloudTrail:** Multi-region logging with log file validation

**All scripts:**
- Discover enabled regions dynamically
- Are idempotent and safe to re-run
- Include verbose comments for quick customization

**🆕 New Features:**
- 🚀 **Unified CLI:** Single `awssec` command for all tools
- 📚 **Comprehensive Documentation:** Detailed guides for each tool
- 🏗️ **Modern Package Structure:** Professional Python package with proper entry points
- 🔧 **Development Tools:** Pre-commit hooks, linting, and testing framework

---

## 🚀 Unified CLI Interface

In addition to the individual scripts, you can now use the unified CLI for a streamlined experience:

```bash
# Install the package
pip install -e .

# Use the unified awssec command
awssec guardduty enable --apply
awssec securityhub enable --apply  
awssec s3-bpa enforce --apply
awssec iam-mfa report
awssec sg audit
awssec cloudtrail enable --apply

# Get help for any command
awssec --help
awssec guardduty --help
```

## 📚 Comprehensive Documentation

Each tool now has detailed documentation with examples, troubleshooting, and best practices:

- 📖 **[Complete Documentation Index](docs/index.md)** - Overview and getting started
- 🛡️ **[GuardDuty Documentation](docs/tools/guardduty.md)** - Threat detection setup
- 🔍 **[Security Hub Documentation](docs/tools/securityhub.md)** - Centralized security management
- 🔒 **[S3 Block Public Access Documentation](docs/tools/s3_bpa.md)** - S3 security hardening
- 🔑 **[IAM MFA Documentation](docs/tools/iam_mfa.md)** - Multi-factor authentication enforcement
- 🔥 **[Security Groups Documentation](docs/tools/sg_audit.md)** - Network security auditing
- 📊 **[CloudTrail Documentation](docs/tools/cloudtrail.md)** - API logging and monitoring

---

## Design Goals

- **Practical:** Minimal flags, sensible defaults, copy-paste commands
- **Safe:** Dry-run where changes are risky, granular `--apply` gates
- **Portable:** Standard boto3, no external infra required
- **Ops-ready:** Easy to wrap in Lambda/EventBridge or CI pipelines

---

## Prerequisites

- Python 3.9+ (tested on 3.11/3.12)
- AWS credentials with sufficient permissions  
  _(use AWS_PROFILE, ~/.aws/credentials, or environment variables)_
- boto3 / botocore

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# or
pip install boto3 botocore
```

---

## Install

```bash
git clone https://github.com/<you>/<repo>.git
cd <repo>
pip install -r requirements.txt
```

_If `requirements.txt` isn’t present, install `boto3` and `botocore` directly._

---

## Usage (One-liners)

### Option 1: Unified CLI (Recommended)
```bash
# Install the package first
pip install -e .

# Use the unified awssec command
awssec guardduty enable --apply
awssec securityhub enable --apply
awssec s3-bpa enforce --apply
awssec iam-mfa report
awssec sg audit
awssec cloudtrail enable --apply
```

### Option 2: Individual Scripts (Legacy)
```bash
# (Optional) choose a profile
export AWS_PROFILE=my-sec-prod

# 1) GuardDuty everywhere
python enable_guardduty_all_regions.py

# 2) Security Hub + standards
python enable_securityhub_all_regions.py

# 3) S3 account & bucket public access block
python s3_block_public_access_everywhere.py            # dry-run per-bucket
python s3_block_public_access_everywhere.py --apply    # enforce per-bucket PAB

# 4) IAM non-MFA report (and optional key disable)
python iam_enforce_mfa_report_and_disable_keys.py > no-mfa-report.csv
python iam_enforce_mfa_report_and_disable_keys.py --apply

# 5) Security Groups: audit & fix open sensitive ports
python ec2_sg_audit_and_fix_open_ports.py
python ec2_sg_audit_and_fix_open_ports.py --apply --ports 22,3389

# 6) CloudTrail multi-region with validation
python cloudtrail_enable_multiregion.py                      # creates secure bucket
python cloudtrail_enable_multiregion.py --bucket my-logs-bkt  # use existing bucket
```

---

## Scripts Overview

### 1. GuardDuty Everywhere

**File:** `enable_guardduty_all_regions.py` | **📖 [Detailed Documentation](docs/tools/guardduty.md)**  
Enables/ensures a GuardDuty detector exists in every enabled region. Attempts to enable Kubernetes audit logs, S3 protection, and EBS malware scanning where supported. *Idempotent.*

**Quick Usage:**
```bash
python enable_guardduty_all_regions.py
# or via unified CLI: awssec guardduty enable --apply
```

**Validate:**  
Console → GuardDuty (per region) shows Enabled; or:
```bash
aws guardduty list-detectors --region us-east-1
```

---

### 2. Security Hub Everywhere + Standards

**File:** `enable_securityhub_all_regions.py` | **📖 [Detailed Documentation](docs/tools/securityhub.md)**  
Enables Security Hub in each enabled region and subscribes to:
- AWS Foundational Security Best Practices (FSBP)
- CIS AWS Foundations Benchmark v1.4

**Quick Usage:**
```bash
python enable_securityhub_all_regions.py
# or via unified CLI: awssec securityhub enable --apply
```

**Validate:**
```bash
aws securityhub get-enabled-standards --region us-west-2
```

---

### 3. S3 Block Public Access (Account + Buckets)

**File:** `s3_block_public_access_everywhere.py` | **📖 [Detailed Documentation](docs/tools/s3_bpa.md)**  
Enforces account-level S3 Block Public Access (BPA) and bucket-level BPA on all buckets. Warns if a bucket policy looks public. Use `--apply` to enforce bucket-level changes; default is dry-run.

**Quick Usage:**
```bash
python s3_block_public_access_everywhere.py --apply
# or via unified CLI: awssec s3-bpa enforce --apply
```

**Validate:**
```bash
aws s3control get-public-access-block --account-id <acct>
aws s3api get-public-access-block --bucket <bucket>
```
**Note:** If you host static sites, prefer CloudFront + OAC and keep buckets private.

---

### 4. IAM: Report Non-MFA Users (Optional Key Disable)

**File:** `iam_enforce_mfa_report_and_disable_keys.py`  
Prints `User,HasMFA,ActiveKeys,KeysDisabled` to stdout. With `--apply`, disables active access keys for users without MFA.

**Validate:**  
Re-run report; or:
```bash
aws iam list-access-keys --user-name <User>
```
**Recommend:** Pair with a global “deny unless MFA” policy (exempt break-glass roles).

---

### 5. EC2 Security Groups: Audit & Fix Open Ports

**File:** `ec2_sg_audit_and_fix_open_ports.py` | **📖 [Detailed Documentation](docs/tools/sg_audit.md)**  
Finds SG rules exposing sensitive ports (default: 22,3389,3306,5432,6379,9200,27017,25) to `0.0.0.0/0` or `::/0`. With `--apply`, revokes only the matching ingress rules.

**Quick Usage:**
```bash
python ec2_sg_audit_and_fix_open_ports.py --apply --ports 22,3389
# or via unified CLI: awssec sg audit
```

**Customize ports:** `--ports 22,3389`

**Validate:** Inspect SG after run:
```bash
aws ec2 describe-security-groups --group-ids <sg> --region <r>
```

---

### 6. CloudTrail: Multi-Region With Validation

**File:** `cloudtrail_enable_multiregion.py` | **📖 [Detailed Documentation](docs/tools/cloudtrail.md)**  
Ensures a multi-region trail (`org-secure-trail`) with log file validation and global events. Creates or secures an S3 bucket (BPA on, SSE-S3, minimal delivery policy).

**Quick Usage:**
```bash
python cloudtrail_enable_multiregion.py
# or via unified CLI: awssec cloudtrail enable --apply
```

**Validate:**
```bash
aws cloudtrail describe-trails --include-shadow-trails false --region us-east-1
aws cloudtrail get-trail-status --name org-secure-trail --region us-east-1
```

---

## Least-Privilege IAM

Attach the following task-role statements to the identity that runs each script. Combine as needed.

- **GuardDuty:**  
  `ec2:DescribeRegions`, `guardduty:*` (Create/Update/List as used), `sts:GetCallerIdentity`
- **Security Hub:**  
  `ec2:DescribeRegions`, `securityhub:EnableSecurityHub`, `securityhub:BatchEnableStandards`, `securityhub:Describe*`, `sts:GetCallerIdentity`
- **S3 BPA:**  
  `s3control:Put/GetPublicAccessBlock`, `s3:ListAllMyBuckets`, `s3:Get/PutBucketPolicy`, `s3:Get/PutPublicAccessBlock`, `sts:GetCallerIdentity`
- **IAM MFA:**  
  `iam:ListUsers`, `iam:ListMFADevices`, `iam:ListAccessKeys`, `iam:UpdateAccessKey`
- **SG Audit/Fix:**  
  `ec2:DescribeRegions`, `ec2:DescribeSecurityGroups`, `ec2:RevokeSecurityGroupIngress`
- **CloudTrail:**  
  `cloudtrail:DescribeTrails/CreateTrail/UpdateTrail/StartLogging`, plus S3 create/policy/encryption permissions and `sts:GetCallerIdentity`

_See each script’s header comments for JSON policy snippets if you want exact statements._

---

## Recommended Run Order

1. CloudTrail → multi-region logging + validation
2. GuardDuty → detectors + data sources
3. Security Hub → enable + FSBP/CIS standards
4. S3 BPA → account & bucket lockdown
5. IAM MFA → report → optionally disable non-MFA keys
6. SG Audit/Fix → report → revoke risky ingress

---

## Automation (Lambda + EventBridge)

- Package any script as a Lambda (Python 3.12) with boto3 (AWS maintains a version in runtime).
- Trigger with EventBridge (e.g., daily at 02:00 UTC) to auto-heal drift and catch new regions.
- Logging & Alerts: Send stdout/stderr to CloudWatch Logs; add metric filters for “FIXED”/“WARNING”; notify via SNS/Slack.
- For Prod, require manual approval (e.g., CodePipeline manual gate) before `--apply`.

---

## Multi-Account / Organizations

Consider delegated admin patterns:
- **GuardDuty:** delegated admin + auto-enable members
- **Security Hub:** central admin + auto-enable standards for members
- **CloudTrail:** org trail (not included here by design)

Run these per-account, or extend with org APIs for fleet-wide enforcement.

---

## Safety, Rollback & Notes

- Dry-run defaults for S3 bucket enforcement and SG remediation; add `--apply` to make changes.
- **Idempotency:** Re-running is safe; scripts only create/update missing or incorrect pieces.

**Rollback:**
- GuardDuty/Security Hub: disable per region
- S3 BPA: delete bucket/account PAB (not recommended)
- IAM keys: re-activate specific key(s)
- SG rules: re-authorize needed ingress
- CloudTrail: stop logging / delete trail

**Public websites:** Prefer CloudFront + OAC instead of public S3 buckets.

**Break-glass:** Keep at least one MFA-protected admin role and test access before enforcing global MFA policies elsewhere.

---

## Project Structure

```
.
├─ src/awssec/                   # Main package
│  ├─ __init__.py
│  ├─ cli.py                     # Unified CLI interface
│  ├─ sessions.py                # AWS session management
│  ├─ utils.py                   # Shared utilities
│  └─ tools/                     # Individual security tools
│     ├─ cloudtrail.py
│     ├─ guardduty.py
│     ├─ securityhub.py
│     ├─ s3_bpa.py
│     ├─ iam_mfa.py
│     └─ sg_audit.py
├─ scripts/                      # Backward-compatible script shims
│  ├─ cloudtrail_enable.py
│  ├─ guardduty_enable.py
│  ├─ securityhub_enable.py
│  ├─ s3_block_public_access.py
│  ├─ iam_mfa_enforce.py
│  └─ security_group_audit_fix.py
├─ docs/                         # Comprehensive documentation
│  ├─ index.md                   # Main documentation landing page
│  └─ tools/                     # Tool-specific documentation
│     ├─ cloudtrail.md
│     ├─ guardduty.md
│     ├─ securityhub.md
│     ├─ s3_bpa.md
│     ├─ iam_mfa.md
│     └─ sg_audit.md
├─ examples/                     # Usage examples and runbooks
├─ tests/                        # Test suite
├─ pyproject.toml               # Package configuration
├─ requirements.txt             # Runtime dependencies
├─ requirements-dev.txt         # Development dependencies
├─ .pre-commit-config.yaml      # Code quality hooks
└─ README.md                    # This file

# Legacy files (still functional):
├─ enable_guardduty_all_regions.py
├─ enable_securityhub_all_regions.py
├─ s3_block_public_access_everywhere.py
├─ iam_enforce_mfa_report_and_disable_keys.py
├─ ec2_sg_audit_and_fix_open_ports.py
└─ cloudtrail_enable_multiregion.py
```

**New Package Features:**
- **Unified CLI:** `awssec` command with subcommands for each tool
- **Modular Design:** Individual tools can be imported and used programmatically
- **Comprehensive Documentation:** Detailed guides with examples and troubleshooting
- **Development Tooling:** Linting, formatting, and testing framework

---

## Contributing

Issues and PRs welcome! Please include:
- Clear description of the posture gap addressed
- Region/Service nuances (and fallbacks)
- Idempotent behavior & dry-run path (if applicable)
- Minimal IAM changes needed

---

## License & Disclaimer

**License:** MIT

**Disclaimer:** Use at your own risk. These scripts make security-impacting changes when `--apply` is used. Test in non-production first and ensure you have appropriate approvals and backups.

---

Happy hardening!  
If you want add-ons (e.g., AWS Config everywhere or SSM patch baselines + maintenance windows), open an issue and we’ll add them in the same style.
