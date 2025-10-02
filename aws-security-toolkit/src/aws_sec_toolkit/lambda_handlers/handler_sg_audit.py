"""Lambda handler for Security Group audit operations."""

import json
import logging
from typing import Any, Dict

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for Security Group audit and fix."""
    try:
        # Import here to avoid cold start issues
        from aws_sec_toolkit.scripts.sg_audit_fix import audit_security_groups, fix_open_security_groups
        
        logger.info("Starting Security Group audit")
        
        # Always audit first
        audit_result = audit_security_groups()
        logger.info(f"Security Group audit completed. Results: {audit_result}")
        
        # Check if we should also fix issues (based on event parameter)
        should_fix = event.get('fix_issues', False)
        fix_result = {}
        
        if should_fix:
            logger.info("Fixing open security groups")
            fix_result = fix_open_security_groups(dry_run=False)
            logger.info(f"Security Group fix completed. Results: {fix_result}")
        
        # Calculate summary statistics
        total_issues = sum(len(issues) for issues in audit_result.values())
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Security Group audit completed successfully',
                'audit_results': audit_result,
                'fix_results': fix_result if should_fix else {},
                'total_issues_found': total_issues,
                'regions_with_issues': len([r for r, issues in audit_result.items() if issues]),
                'fixes_applied': should_fix,
                'successful_fixes': sum(1 for success in fix_result.values() if success) if should_fix else 0
            })
        }
        
    except Exception as e:
        logger.error(f"Error in Security Group audit: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to audit Security Groups'
            })
        }