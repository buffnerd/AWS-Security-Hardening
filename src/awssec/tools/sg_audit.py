"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Find inbound 0.0.0.0/0 risks and offer safe remediations.
"""

import logging
from typing import Dict, List, Optional, Tuple
import boto3
from botocore.exceptions import ClientError

from ..sessions import get_session
from ..utils import retry_on_throttle, get_all_regions, print_status

logger = logging.getLogger(__name__)

# Risky ports that should not be open to 0.0.0.0/0
RISKY_PORTS = [22, 3389, 1433, 3306, 5432, 6379, 27017, 5984, 9200, 11211]


@retry_on_throttle(max_retries=3)
def audit_security_groups(
    session: boto3.Session,
    regions: Optional[List[str]] = None,
    risky_ports: Optional[List[int]] = None
) -> Dict[str, List[Dict]]:
    """Audit security groups for risky inbound rules."""
    if regions is None:
        regions = get_all_regions(session)
    
    if risky_ports is None:
        risky_ports = RISKY_PORTS
    
    findings = {}
    
    for region in regions:
        try:
            ec2 = session.client("ec2", region_name=region)
            findings[region] = []
            
            # Get all security groups
            paginator = ec2.get_paginator('describe_security_groups')
            
            for page in paginator.paginate():
                for sg in page['SecurityGroups']:
                    sg_id = sg['GroupId']
                    sg_name = sg['GroupName']
                    vpc_id = sg.get('VpcId', 'EC2-Classic')
                    
                    # Check inbound rules
                    for rule in sg.get('IpPermissions', []):
                        from_port = rule.get('FromPort')
                        to_port = rule.get('ToPort')
                        protocol = rule.get('IpProtocol', 'unknown')
                        
                        # Check for 0.0.0.0/0 ranges
                        for ip_range in rule.get('IpRanges', []):
                            cidr = ip_range.get('CidrIp')
                            
                            if cidr == '0.0.0.0/0':
                                # Check if any risky ports are exposed
                                exposed_risky_ports = []
                                
                                if protocol == '-1':  # All protocols
                                    exposed_risky_ports = risky_ports
                                elif protocol in ['tcp', 'udp'] and from_port is not None and to_port is not None:
                                    for port in risky_ports:
                                        if from_port <= port <= to_port:
                                            exposed_risky_ports.append(port)
                                elif protocol in ['tcp', 'udp'] and from_port in risky_ports:
                                    exposed_risky_ports.append(from_port)
                                
                                if exposed_risky_ports or cidr == '0.0.0.0/0':
                                    findings[region].append({
                                        'security_group_id': sg_id,
                                        'security_group_name': sg_name,
                                        'vpc_id': vpc_id,
                                        'protocol': protocol,
                                        'from_port': from_port,
                                        'to_port': to_port,
                                        'cidr': cidr,
                                        'risky_ports_exposed': exposed_risky_ports,
                                        'severity': 'HIGH' if exposed_risky_ports else 'MEDIUM'
                                    })
        
        except ClientError as e:
            print_status(f"Failed to audit security groups in {region}: {e}", 'ERROR')
            findings[region] = [{'error': str(e)}]
        except Exception as e:
            print_status(f"Unexpected error in {region}: {e}", 'ERROR')
            findings[region] = [{'error': str(e)}]
    
    return findings


@retry_on_throttle(max_retries=3)
def fix_security_group_rules(
    session: boto3.Session,
    findings: Dict[str, List[Dict]],
    replacement_cidrs: List[str] = None,
    dry_run: bool = False
) -> Dict[str, Dict[str, bool]]:
    """Fix risky security group rules by replacing 0.0.0.0/0 with specific CIDRs."""
    if replacement_cidrs is None:
        replacement_cidrs = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']  # Private ranges
    
    results = {}
    
    for region, region_findings in findings.items():
        if not region_findings or 'error' in region_findings[0]:
            continue
        
        results[region] = {}
        ec2 = session.client("ec2", region_name=region)
        
        for finding in region_findings:
            sg_id = finding['security_group_id']
            protocol = finding['protocol']
            from_port = finding['from_port']
            to_port = finding['to_port']
            
            try:
                # First, revoke the risky rule
                revoke_params = {
                    'GroupId': sg_id,
                    'IpPermissions': [{
                        'IpProtocol': protocol,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }]
                }
                
                if from_port is not None:
                    revoke_params['IpPermissions'][0]['FromPort'] = from_port
                if to_port is not None:
                    revoke_params['IpPermissions'][0]['ToPort'] = to_port
                
                if not dry_run:
                    ec2.revoke_security_group_ingress(**revoke_params)
                    print_status(f"Revoked risky rule from {sg_id} in {region}", 'SUCCESS')
                else:
                    print_status(f"Would revoke risky rule from {sg_id} in {region}", 'WARNING', dry_run)
                
                # Then, add replacement rules with safer CIDRs
                for cidr in replacement_cidrs:
                    authorize_params = {
                        'GroupId': sg_id,
                        'IpPermissions': [{
                            'IpProtocol': protocol,
                            'IpRanges': [{'CidrIp': cidr, 'Description': 'Replaced risky 0.0.0.0/0 rule'}]
                        }]
                    }
                    
                    if from_port is not None:
                        authorize_params['IpPermissions'][0]['FromPort'] = from_port
                    if to_port is not None:
                        authorize_params['IpPermissions'][0]['ToPort'] = to_port
                    
                    if not dry_run:
                        ec2.authorize_security_group_ingress(**authorize_params)
                        print_status(f"Added safer rule {cidr} to {sg_id} in {region}", 'SUCCESS')
                    else:
                        print_status(f"Would add safer rule {cidr} to {sg_id} in {region}", 'INFO', dry_run)
                
                results[region][sg_id] = True
                
            except ClientError as e:
                print_status(f"Failed to fix security group {sg_id} in {region}: {e}", 'ERROR')
                results[region][sg_id] = False
            except Exception as e:
                print_status(f"Unexpected error fixing {sg_id} in {region}: {e}", 'ERROR')
                results[region][sg_id] = False
    
    return results


def audit_and_fix_security_groups(
    session: boto3.Session,
    regions: Optional[List[str]] = None,
    risky_ports: Optional[List[int]] = None,
    fix_rules: bool = False,
    replacement_cidrs: Optional[List[str]] = None,
    dry_run: bool = False
) -> Dict[str, any]:
    """Comprehensive security group audit and remediation."""
    results = {}
    
    # Audit phase
    print_status("Starting security group audit...", 'INFO')
    findings = audit_security_groups(session, regions, risky_ports)
    
    # Count total findings
    total_findings = sum(len(region_findings) for region_findings in findings.values())
    results['audit'] = findings
    results['total_findings'] = total_findings
    
    print_status(f"Found {total_findings} risky security group rules", 'WARNING' if total_findings > 0 else 'SUCCESS')
    
    # Fix phase (if requested)
    if fix_rules and total_findings > 0:
        print_status("Starting security group remediation...", 'INFO')
        fix_results = fix_security_group_rules(session, findings, replacement_cidrs, dry_run)
        results['fixes'] = fix_results
    
    return results