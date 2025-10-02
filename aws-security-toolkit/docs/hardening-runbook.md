# AWS Security Hardening Runbook

This document outlines the safe order of operations for implementing AWS security hardening measures.

## Pre-Execution Checklist

- [ ] Review current AWS environment configuration
- [ ] Ensure appropriate backup procedures are in place
- [ ] Verify IAM permissions for executing security changes
- [ ] Test in non-production environment first
- [ ] Communicate changes to stakeholders

## Recommended Execution Order

### Phase 1: Monitoring and Logging
1. **CloudTrail** - Enable comprehensive logging first
2. **GuardDuty** - Enable threat detection
3. **Security Hub** - Centralize security findings

### Phase 2: Identity and Access Management
4. **IAM MFA Enforcement** - Secure user access
5. **IAM Access Key Audit** - Disable unnecessary keys

### Phase 3: Network and Resource Security
6. **Security Group Audit** - Review and fix open ports
7. **S3 Block Public Access** - Prevent data exposure

## Rollback Procedures

### CloudTrail Rollback
```bash
# Disable CloudTrail if needed
aws cloudtrail stop-logging --name <trail-name>
aws cloudtrail delete-trail --name <trail-name>
```

### GuardDuty Rollback
```bash
# Disable GuardDuty detector
aws guardduty delete-detector --detector-id <detector-id>
```

### Security Hub Rollback
```bash
# Disable Security Hub
aws securityhub disable-security-hub
```

### IAM MFA Rollback
- Re-enable access keys manually through AWS Console
- Remove MFA requirements from policies

### Security Group Rollback
- Restore original security group rules from backup
- Test connectivity after restoration

### S3 Public Access Rollback
```bash
# Remove block public access if needed
aws s3api delete-public-access-block --bucket <bucket-name>
```

## Safety Considerations

1. **Always test in dev/staging first**
2. **Maintain configuration backups**
3. **Monitor for service disruptions**
4. **Have rollback procedures ready**
5. **Coordinate with application teams**
6. **Document all changes made**

## Emergency Contacts

- Cloud Security Team: security@company.com
- DevOps Team: devops@company.com
- On-Call Engineer: +1-xxx-xxx-xxxx