#!/usr/bin/env python3
"""
Example script demonstrating common patterns for AWS security scripts.

This example shows:
- How to use the shared utility functions
- Common argument parsing patterns
- Error handling approaches
- Logging configuration
"""

import sys
import os
import argparse

# Add parent directory to path for utils import
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from utils import (
    setup_logging,
    get_aws_session,
    get_enabled_regions,
    get_account_id,
    handle_aws_error,
    confirm_action
)


def process_region(session, region: str, dry_run: bool) -> dict:
    """
    Example function that processes a single AWS region.
    
    Args:
        session: boto3.Session instance
        region: AWS region to process
        dry_run: If True, only show what would be done
    
    Returns:
        Dictionary with results
    """
    import logging
    logger = logging.getLogger(__name__)
    
    result = {
        'region': region,
        'success': False,
        'message': ''
    }
    
    try:
        # Example: List EC2 instances in region
        ec2 = session.client('ec2', region_name=region)
        
        if dry_run:
            logger.info(f"[DRY-RUN] Would process region {region}")
            result['message'] = "Dry run - no changes made"
        else:
            response = ec2.describe_instances()
            instance_count = sum(
                len(reservation['Instances']) 
                for reservation in response['Reservations']
            )
            result['message'] = f"Found {instance_count} instances"
            logger.info(f"Region {region}: {instance_count} instances")
        
        result['success'] = True
        
    except Exception as e:
        handle_aws_error(e, f"Error processing region {region}")
        result['message'] = str(e)
    
    return result


def main():
    """Main execution function."""
    # Argument parsing
    parser = argparse.ArgumentParser(
        description='Example AWS security script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all enabled regions
  python example_script.py
  
  # Use specific AWS profile
  python example_script.py --profile production
  
  # Dry-run mode
  python example_script.py --dry-run
  
  # Process specific regions only
  python example_script.py --regions us-east-1,us-west-2
  
  # Enable debug logging
  python example_script.py --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '--profile',
        help='AWS CLI profile to use'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--regions',
        help='Comma-separated list of regions to process'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("Starting AWS security script...")
    
    # Create AWS session
    try:
        session = get_aws_session(profile=args.profile)
        account_id = get_account_id(session)
        logger.info(f"AWS Account ID: {account_id}")
    except Exception as e:
        logger.error(f"Failed to create AWS session: {e}")
        return 1
    
    # Determine regions to process
    if args.regions:
        regions = [r.strip() for r in args.regions.split(',')]
        logger.info(f"Processing specified regions: {', '.join(regions)}")
    else:
        regions = get_enabled_regions(session)
        logger.info(f"Processing all enabled regions ({len(regions)} total)")
    
    if not regions:
        logger.error("No regions to process")
        return 1
    
    # Confirmation prompt (unless --no-confirm)
    if not args.no_confirm and not args.dry_run:
        message = f"Proceed with processing {len(regions)} region(s)?"
        if not confirm_action(message):
            logger.info("Operation cancelled by user")
            return 0
    
    # Process each region
    logger.info("\n" + "="*60)
    logger.info("Processing Regions")
    logger.info("="*60)
    
    results = []
    for region in regions:
        logger.info(f"\nProcessing: {region}")
        result = process_region(session, region, args.dry_run)
        results.append(result)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("SUMMARY")
    logger.info("="*60)
    
    success_count = sum(1 for r in results if r['success'])
    failure_count = len(results) - success_count
    
    logger.info(f"Total regions processed: {len(results)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed: {failure_count}")
    
    if failure_count > 0:
        logger.warning("\nFailed regions:")
        for result in results:
            if not result['success']:
                logger.warning(f"  {result['region']}: {result['message']}")
    
    # Return exit code
    return 0 if failure_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
