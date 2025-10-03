"""
██████╗░██╗░░░██╗███████╗███████╗  ███╗░░██╗███████╗██████╗░██████╗░
██╔══██╗██║░░░██║██╔════╝██╔════╝  ████╗░██║██╔════╝██╔══██╗██╔══██╗
██████╦╝██║░░░██║█████╗░░█████╗░░  ██╔██╗██║█████╗░░██████╔╝██║░░██║
██╔══██╗██║░░░██║██╔══╝░░██╔══╝░░  ██║╚████║██╔══╝░░██╔══██╗██║░░██║
██████╦╝╚██████╔╝██║░░░░░██║░░░░░  ██║░╚███║███████╗██║░░██║██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝░░░░░  ╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝╚═════╝░
-------Scripts by Aaron Voborny---https://github.com/buffnerd-------
Utilities for AWS operations: pagination, retry, output formatting, logging.
"""

import logging
import time
import json
import csv
import io
from typing import Generator, Dict, Any, List, Optional, Callable
from functools import wraps
from botocore.exceptions import ClientError
import boto3


def setup_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """Set up a logger with consistent formatting."""
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set level
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    logger.setLevel(log_levels.get(level.upper(), logging.INFO))
    
    # Create handler and formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def paginate(client, operation: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
    """
    Paginate through AWS API responses.
    
    Args:
        client: boto3 client
        operation: Operation name (e.g., 'list_buckets')
        **kwargs: Operation parameters
        
    Yields:
        Individual items from paginated responses
    """
    paginator = client.get_paginator(operation)
    
    for page in paginator.paginate(**kwargs):
        # Determine the key that contains the list of items
        # This is usually the operation name without 'list_' prefix, pluralized
        for key, value in page.items():
            if isinstance(value, list) and key != 'ResponseMetadata':
                for item in value:
                    yield item
                break


def retry_on_throttle(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator to retry AWS operations on throttling errors.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries (exponential backoff)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    
                    if error_code in ['Throttling', 'ThrottlingException', 'RequestLimitExceeded']:
                        if attempt < max_retries:
                            delay = base_delay * (2 ** attempt)
                            logging.warning(f"Throttled, retrying in {delay}s (attempt {attempt + 1}/{max_retries + 1})")
                            time.sleep(delay)
                            last_exception = e
                            continue
                    
                    # Re-raise if not a throttling error or max retries exceeded
                    raise
                except Exception as e:
                    # Re-raise non-ClientError exceptions immediately
                    raise
            
            # If we get here, we've exhausted retries
            raise last_exception
        
        return wrapper
    return decorator


def format_output(data: Any, output_format: str = 'table') -> str:
    """
    Format data for output in various formats.
    
    Args:
        data: Data to format
        output_format: Output format ('table', 'json', 'csv')
        
    Returns:
        Formatted string
    """
    if output_format == 'json':
        return json.dumps(data, indent=2, default=str)
    
    elif output_format == 'csv':
        if not isinstance(data, list):
            data = [data]
        
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    elif output_format == 'table':
        return format_table(data)
    
    else:
        return str(data)


def format_table(data: Any) -> str:
    """Format data as a simple table."""
    if not data:
        return "No data to display"
    
    if isinstance(data, dict):
        # Single dictionary - show as key-value pairs
        lines = []
        for key, value in data.items():
            lines.append(f"{key:20} {value}")
        return "\n".join(lines)
    
    elif isinstance(data, list) and data:
        if isinstance(data[0], dict):
            # List of dictionaries - show as table
            headers = list(data[0].keys())
            
            # Calculate column widths
            widths = {header: len(header) for header in headers}
            for item in data:
                for header in headers:
                    widths[header] = max(widths[header], len(str(item.get(header, ''))))
            
            # Format header
            header_line = " | ".join(header.ljust(widths[header]) for header in headers)
            separator = "-" * len(header_line)
            
            # Format rows
            lines = [header_line, separator]
            for item in data:
                row = " | ".join(str(item.get(header, '')).ljust(widths[header]) for header in headers)
                lines.append(row)
            
            return "\n".join(lines)
    
    return str(data)


def get_all_regions(session: boto3.Session) -> List[str]:
    """Get all AWS regions."""
    try:
        ec2 = session.client('ec2')
        response = ec2.describe_regions()
        return [region['RegionName'] for region in response['Regions']]
    except Exception as e:
        logging.error(f"Failed to get regions: {e}")
        return [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
            'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-central-1',
            'ap-northeast-1', 'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2',
            'ap-south-1', 'ca-central-1', 'sa-east-1'
        ]


def print_status(message: str, status: str = 'INFO', dry_run: bool = False):
    """Print colored status messages."""
    colors = {
        'SUCCESS': '\033[92m',  # Green
        'ERROR': '\033[91m',    # Red
        'WARNING': '\033[93m',  # Yellow
        'INFO': '\033[94m',     # Blue
        'DRY_RUN': '\033[95m'   # Magenta
    }
    
    reset = '\033[0m'
    
    if dry_run:
        status = 'DRY_RUN'
        message = f"[DRY RUN] {message}"
    
    color = colors.get(status, '')
    print(f"{color}[{status}]{reset} {message}")


def safe_get(dictionary: dict, *keys, default=None):
    """Safely get nested dictionary values."""
    for key in keys:
        try:
            dictionary = dictionary[key]
        except (KeyError, TypeError):
            return default
    return dictionary