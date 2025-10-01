# IAM Security Scripts

Scripts for Identity and Access Management security hardening and compliance.

## Planned Scripts

### Password Policy Management
- `enforce_password_policy.py` - Set strong password policies for IAM users
- `audit_password_policy.py` - Check password policy compliance

### MFA Management
- `audit_mfa_compliance.py` - Check which users have MFA enabled
- `require_mfa.py` - Enforce MFA for IAM users
- `disable_console_without_mfa.py` - Disable console access for users without MFA

### Access Key Management
- `audit_access_keys.py` - Find old or unused access keys
- `rotate_access_keys.py` - Automated access key rotation
- `disable_inactive_keys.py` - Disable keys not used in X days

### Role and Policy Management
- `audit_unused_roles.py` - Find roles that haven't been used
- `audit_overprivileged_roles.py` - Identify overly permissive roles
- `audit_inline_policies.py` - Find and report inline policies
- `generate_least_privilege_policy.py` - Generate policies based on CloudTrail logs

### User Management
- `audit_root_account.py` - Check root account usage and security
- `list_admin_users.py` - Identify users with administrative access
- `disable_inactive_users.py` - Disable users inactive for X days

## Required IAM Permissions

Scripts in this category typically require:
- `iam:Get*`
- `iam:List*`
- `iam:UpdateAccountPasswordPolicy`
- `iam:GenerateCredentialReport`
