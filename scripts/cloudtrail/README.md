# CloudTrail Security Scripts

Scripts for managing AWS CloudTrail logging and monitoring.

## Planned Scripts

### Trail Management
- `enable_cloudtrail.py` - Enable CloudTrail in all regions
- `create_organization_trail.py` - Setup organization-wide trail
- `audit_trail_configuration.py` - Check trail configurations

### Log Security
- `enable_log_file_validation.py` - Enable log file integrity validation
- `configure_log_encryption.py` - Setup KMS encryption for logs
- `setup_log_monitoring.py` - Configure CloudWatch Logs integration

### Compliance
- `audit_trail_status.py` - Check if trails are logging properly
- `verify_multi_region_trails.py` - Ensure multi-region trails exist
- `check_management_events.py` - Verify management events are logged

## Required IAM Permissions

Scripts in this category typically require:
- `cloudtrail:DescribeTrails`
- `cloudtrail:GetTrailStatus`
- `cloudtrail:CreateTrail`
- `cloudtrail:UpdateTrail`
- `cloudtrail:StartLogging`
