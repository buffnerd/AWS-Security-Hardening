#!/usr/bin/env python3
"""
Enable Amazon GuardDuty in all enabled regions.

This script enables (or re-enables) Amazon GuardDuty across all enabled regions
in your AWS account. It also attempts to enable useful data sources including:
- S3 Protection
- EBS Malware Protection
- Kubernetes Protection

Usage:
    python enable_guardduty.py [--profile PROFILE] [--dry-run]

Options:
    --profile PROFILE   AWS CLI profile to use
    --dry-run          Show what would be done without making changes
    --regions REGIONS  Comma-separated list of regions (default: all enabled)
"""

import sys
import os
import argparse
import logging
from typing import List, Dict

# Add parent directory to path for utils import
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, parent_dir)

from utils import (
    setup_logging,
    get_aws_session,
    get_enabled_regions,
    get_account_id,
    handle_aws_error
)


def enable_guardduty_in_region(session, region: str, dry_run: bool = False) -> Dict:
    """
    Enable GuardDuty in a specific region.
    
    Args:
        session: boto3.Session instance
        region: AWS region name
        dry_run: If True, only show what would be done
    
    Returns:
        Dictionary with status information
    """
    result = {
        'region': region,
        'enabled': False,
        'detector_id': None,
        's3_protection': False,
        'ebs_protection': False,
        'kubernetes_protection': False,
        'errors': []
    }
    
    guardduty = session.client('guardduty', region_name=region)
    logger = logging.getLogger(__name__)
    
    try:
        # Check for existing detectors
        response = guardduty.list_detectors()
        
        if response['DetectorIds']:
            detector_id = response['DetectorIds'][0]
            result['detector_id'] = detector_id
            result['enabled'] = True
            logger.info(f"GuardDuty already enabled in {region} (Detector: {detector_id})")
        else:
            if dry_run:
                logger.info(f"[DRY-RUN] Would enable GuardDuty in {region}")
            else:
                # Create new detector
                response = guardduty.create_detector(Enable=True)
                detector_id = response['DetectorId']
                result['detector_id'] = detector_id
                result['enabled'] = True
                logger.info(f"GuardDuty enabled in {region} (Detector: {detector_id})")
        
        # Enable data sources if detector exists or was created
        if result['detector_id'] and not dry_run:
            try:
                # Enable S3 Protection
                guardduty.update_detector(
                    DetectorId=result['detector_id'],
                    DataSources={
                        'S3Logs': {'Enable': True}
                    }
                )
                result['s3_protection'] = True
                logger.info(f"S3 Protection enabled in {region}")
            except Exception as e:
                error_msg = f"Could not enable S3 Protection: {str(e)}"
                result['errors'].append(error_msg)
                logger.warning(error_msg)
            
            try:
                # Enable EBS Malware Protection
                guardduty.update_malware_protection_plan(
                    DetectorId=result['detector_id'],
                    MalwareProtectionPlan={
                        'ScanEc2InstanceWithFindings': {'EbsVolumes': {'Enable': True}}
                    }
                )
                result['ebs_protection'] = True
                logger.info(f"EBS Malware Protection enabled in {region}")
            except Exception as e:
                error_msg = f"Could not enable EBS Protection: {str(e)}"
                result['errors'].append(error_msg)
                logger.warning(error_msg)
            
            try:
                # Enable Kubernetes Protection
                guardduty.update_detector(
                    DetectorId=result['detector_id'],
                    DataSources={
                        'Kubernetes': {'AuditLogs': {'Enable': True}}
                    }
                )
                result['kubernetes_protection'] = True
                logger.info(f"Kubernetes Protection enabled in {region}")
            except Exception as e:
                error_msg = f"Could not enable Kubernetes Protection: {str(e)}"
                result['errors'].append(error_msg)
                logger.warning(error_msg)
        
    except Exception as e:
        handle_aws_error(e, f"Error in region {region}")
        result['errors'].append(str(e))
    
    return result


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Enable Amazon GuardDuty in all enabled regions'
    )
    parser.add_argument('--profile', help='AWS CLI profile to use')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    parser.add_argument('--regions', help='Comma-separated list of regions')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    # Create AWS session
    session = get_aws_session(profile=args.profile)
    account_id = get_account_id(session)
    logger.info(f"Working on AWS Account: {account_id}")
    
    # Get regions to process
    if args.regions:
        regions = [r.strip() for r in args.regions.split(',')]
    else:
        regions = get_enabled_regions(session)
    
    logger.info(f"Processing {len(regions)} region(s)")
    
    # Process each region
    results = []
    for region in regions:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing region: {region}")
        logger.info(f"{'='*60}")
        
        result = enable_guardduty_in_region(session, region, args.dry_run)
        results.append(result)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")
    
    enabled_count = sum(1 for r in results if r['enabled'])
    logger.info(f"Regions processed: {len(results)}")
    logger.info(f"GuardDuty enabled: {enabled_count}")
    
    if not args.dry_run:
        s3_count = sum(1 for r in results if r['s3_protection'])
        ebs_count = sum(1 for r in results if r['ebs_protection'])
        k8s_count = sum(1 for r in results if r['kubernetes_protection'])
        
        logger.info(f"S3 Protection enabled: {s3_count}")
        logger.info(f"EBS Protection enabled: {ebs_count}")
        logger.info(f"Kubernetes Protection enabled: {k8s_count}")
    
    errors = [r for r in results if r['errors']]
    if errors:
        logger.warning(f"\nRegions with errors: {len(errors)}")
        for result in errors:
            logger.warning(f"  {result['region']}: {', '.join(result['errors'])}")


if __name__ == '__main__':
    main()
