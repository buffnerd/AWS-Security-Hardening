# S3 Security Scripts

Scripts for securing Amazon S3 buckets and enforcing best practices.

## Planned Scripts

### Encryption
- `enable_bucket_encryption.py` - Enable default encryption on all buckets
- `audit_bucket_encryption.py` - Check encryption status of all buckets
- `enforce_ssl_only.py` - Ensure buckets only accept SSL connections

### Public Access
- `block_public_access.py` - Enable Block Public Access on all buckets
- `audit_public_buckets.py` - Find buckets with public access
- `audit_bucket_acls.py` - Review bucket ACL configurations

### Logging and Monitoring
- `enable_bucket_logging.py` - Enable access logging for all buckets
- `enable_bucket_versioning.py` - Enable versioning on buckets
- `configure_lifecycle_policies.py` - Setup lifecycle policies for old logs

### Bucket Policies
- `audit_bucket_policies.py` - Review bucket policy configurations
- `enforce_secure_transport.py` - Add policies requiring secure transport
- `remove_overly_permissive_policies.py` - Identify and remediate permissive policies

### Object Security
- `scan_for_sensitive_data.py` - Scan objects for sensitive information
- `audit_object_permissions.py` - Check object-level permissions

## Required IAM Permissions

Scripts in this category typically require:
- `s3:ListAllMyBuckets`
- `s3:GetBucket*`
- `s3:PutBucket*`
- `s3:GetEncryptionConfiguration`
- `s3:PutEncryptionConfiguration`
