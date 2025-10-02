# Security Group Remediation Notes

This document contains important caveats and recovery procedures for security group remediation.

## Important Caveats

### Before Making Changes

1. **Document existing rules** - Always backup current security group configurations
2. **Identify dependencies** - Map which applications use which security groups
3. **Coordinate with teams** - Notify application owners before changes
4. **Test in staging** - Validate changes in non-production environments first

### Common Risks

- **Application connectivity loss** - Breaking legitimate application communication
- **Load balancer failures** - Disrupting traffic flow to applications
- **Database connection issues** - Breaking application-to-database connectivity
- **Cross-VPC communication** - Affecting peering or transit gateway traffic

## Safe Remediation Approach

### 1. Discovery Phase

```python
def analyze_security_group_usage(sg_id):
    """Analyze what resources are using a security group."""
    ec2 = boto3.client('ec2')
    
    # Find instances using this SG
    instances = ec2.describe_instances(
        Filters=[
            {'Name': 'instance.group-id', 'Values': [sg_id]}
        ]
    )
    
    # Find network interfaces using this SG
    enis = ec2.describe_network_interfaces(
        Filters=[
            {'Name': 'group-id', 'Values': [sg_id]}
        ]
    )
    
    # Find load balancers using this SG
    elbv2 = boto3.client('elbv2')
    load_balancers = elbv2.describe_load_balancers()
    
    return {
        'instances': instances,
        'network_interfaces': enis,
        'load_balancers': load_balancers
    }
```

### 2. Risk Assessment

```python
def assess_remediation_risk(sg_rules):
    """Assess risk level of proposed security group changes."""
    high_risk_ports = [22, 3389, 1433, 3306, 5432, 6379]  # SSH, RDP, DB ports
    critical_cidrs = ['0.0.0.0/0']  # Open to internet
    
    risk_score = 0
    
    for rule in sg_rules:
        if rule.get('FromPort') in high_risk_ports:
            risk_score += 2
        if any(cidr in critical_cidrs for cidr in rule.get('CidrBlocks', [])):
            risk_score += 3
    
    if risk_score >= 5:
        return 'HIGH'
    elif risk_score >= 3:
        return 'MEDIUM'
    else:
        return 'LOW'
```

### 3. Staged Remediation

```python
def safe_security_group_remediation(sg_id, dry_run=True):
    """Safely remediate security group rules."""
    ec2 = boto3.client('ec2')
    
    # Step 1: Backup existing rules
    backup = backup_security_group_rules(sg_id)
    
    # Step 2: Identify problematic rules
    problematic_rules = identify_open_rules(sg_id)
    
    # Step 3: Create temporary restrictive rules (if not dry run)
    if not dry_run:
        for rule in problematic_rules:
            # Add more restrictive rule first
            add_restrictive_rule(sg_id, rule)
            
            # Wait and monitor for issues
            time.sleep(300)  # 5 minute wait
            
            # Check application health
            if check_application_health():
                # Remove original open rule
                remove_open_rule(sg_id, rule)
            else:
                # Rollback - remove restrictive rule
                remove_restrictive_rule(sg_id, rule)
                print(f"Rollback performed for rule: {rule}")
```

## Recovery Procedures

### Emergency Rollback

```bash
# Quick restore of original security group rules
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Or use JSON backup
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --cli-input-json file://sg-backup.json
```

### Systematic Recovery

1. **Immediate Response**
   - Stop all remediation activities
   - Assess scope of impact
   - Notify affected teams

2. **Restore Critical Services**
   - Prioritize business-critical applications
   - Restore database connectivity first
   - Then restore web tier access

3. **Gradual Recovery**
   - Restore rules one at a time
   - Verify application functionality after each restoration
   - Document lessons learned

### Application Health Monitoring

```python
def check_application_health():
    """Check if applications are healthy after SG changes."""
    health_checks = [
        check_web_tier_health(),
        check_database_connectivity(),
        check_load_balancer_targets(),
        check_microservice_communication()
    ]
    
    return all(health_checks)

def check_web_tier_health():
    """Check web tier application health."""
    try:
        response = requests.get('http://health-check-endpoint/status')
        return response.status_code == 200
    except:
        return False
```

## Best Practices

### Planning

1. **Create detailed backup** - Document all existing rules
2. **Map dependencies** - Understand application communication patterns
3. **Define rollback criteria** - Know when to abort and rollback
4. **Prepare monitoring** - Set up health checks and alerts

### Execution

1. **Use dry-run mode first** - Always test changes before applying
2. **Change one rule at a time** - Minimize blast radius
3. **Monitor continuously** - Watch for application issues
4. **Have team on standby** - Ensure quick response capability

### Post-Remediation

1. **Validate application functionality** - Test all affected services
2. **Update documentation** - Record approved security group configurations
3. **Schedule regular reviews** - Prevent drift over time
4. **Implement automation** - Use AWS Config rules for ongoing compliance

## Common Recovery Scenarios

### Scenario 1: Web Application Unreachable

```bash
# Symptoms: HTTP 500 errors, connection timeouts
# Quick fix: Restore load balancer security group rules

aws ec2 authorize-security-group-ingress \
    --group-id sg-lb-12345 \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-id sg-lb-12345 \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0
```

### Scenario 2: Database Connection Failures

```bash
# Symptoms: Database connection errors in application logs
# Quick fix: Restore database security group rules

aws ec2 authorize-security-group-ingress \
    --group-id sg-db-12345 \
    --protocol tcp \
    --port 3306 \
    --source-group sg-app-12345
```

### Scenario 3: SSH Access Lost

```bash
# Symptoms: Cannot connect to instances via SSH
# Quick fix: Restore SSH access (temporarily open, then restrict)

aws ec2 authorize-security-group-ingress \
    --group-id sg-12345 \
    --protocol tcp \
    --port 22 \
    --cidr YOUR_IP/32  # Restrict to your IP only
```

## Monitoring and Alerting

### CloudWatch Alarms

```yaml
# Example CloudWatch alarm for connection failures
AlarmName: HighConnectionErrors
MetricName: ConnectionErrors
Namespace: AWS/ApplicationELB
Statistic: Sum
Period: 300
EvaluationPeriods: 2
Threshold: 10
ComparisonOperator: GreaterThanThreshold
```

### AWS Config Rules

```yaml
# Monitor for overly permissive security groups
ConfigRuleName: security-group-ssh-check
Source:
  Owner: AWS
  SourceIdentifier: INCOMING_SSH_DISABLED
```

## Emergency Contacts

- **Network Team**: network@company.com
- **Application Team**: apps@company.com  
- **Database Team**: dba@company.com
- **Security Team**: security@company.com
- **On-Call Engineer**: +1-xxx-xxx-xxxx