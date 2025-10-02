"""Tests for regions functionality across all scripts."""

import unittest
from unittest.mock import patch, MagicMock, call
import boto3
from moto import mock_aws
import pytest

# Import all the region-related functions from scripts
from aws_sec_toolkit.scripts.guardduty_enable import get_enabled_regions


class TestRegionFunctionality(unittest.TestCase):
    """Test cases for region discovery functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = MagicMock()
        self.mock_ec2 = MagicMock()
        self.mock_session.client.return_value = self.mock_ec2

    def test_get_enabled_regions_success(self):
        """Test successful region discovery."""
        # Mock the describe_regions response
        self.mock_ec2.describe_regions.return_value = {
            'Regions': [
                {'RegionName': 'us-east-1', 'OptInStatus': 'opt-in-not-required'},
                {'RegionName': 'us-west-2', 'OptInStatus': 'opted-in'},
                {'RegionName': 'ap-south-1', 'OptInStatus': 'not-opted-in'},
                {'RegionName': 'eu-west-1', 'OptInStatus': None}  # Default regions
            ]
        }

        result = get_enabled_regions(self.mock_session)
        
        # Should include enabled regions only
        expected_regions = ['us-east-1', 'us-west-2', 'eu-west-1']
        self.assertEqual(sorted(result), sorted(expected_regions))
        
        # Verify the EC2 client was called correctly
        self.mock_session.client.assert_called_with("ec2", region_name="us-east-1", config=unittest.mock.ANY)
        self.mock_ec2.describe_regions.assert_called_once_with(AllRegions=True)

    def test_get_enabled_regions_empty_response(self):
        """Test handling of empty regions response."""
        self.mock_ec2.describe_regions.return_value = {'Regions': []}
        
        result = get_enabled_regions(self.mock_session)
        
        self.assertEqual(result, [])

    def test_get_enabled_regions_filters_disabled(self):
        """Test that disabled regions are filtered out."""
        self.mock_ec2.describe_regions.return_value = {
            'Regions': [
                {'RegionName': 'us-east-1', 'OptInStatus': 'opt-in-not-required'},
                {'RegionName': 'ap-east-1', 'OptInStatus': 'not-opted-in'},
                {'RegionName': 'me-south-1', 'OptInStatus': 'not-opted-in'}
            ]
        }

        result = get_enabled_regions(self.mock_session)
        
        # Should only include us-east-1
        self.assertEqual(result, ['us-east-1'])

    @patch('boto3.Session')
    def test_get_enabled_regions_integration(self, mock_session_class):
        """Test integration with actual boto3 session creation."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_ec2 = MagicMock()
        mock_session.client.return_value = mock_ec2
        
        mock_ec2.describe_regions.return_value = {
            'Regions': [
                {'RegionName': 'us-east-1', 'OptInStatus': 'opt-in-not-required'},
                {'RegionName': 'eu-west-1', 'OptInStatus': 'opted-in'}
            ]
        }

        # Import here to use the patched Session
        from aws_sec_toolkit.scripts.guardduty_enable import enable_guardduty_all_regions
        
        # Mock the GuardDuty calls
        mock_gd = MagicMock()
        mock_session.client.side_effect = lambda service, **kwargs: {
            'ec2': mock_ec2,
            'guardduty': mock_gd
        }[service]
        
        mock_gd.list_detectors.return_value = {'DetectorIds': []}
        mock_gd.create_detector.return_value = {'DetectorId': 'test-detector-id'}
        
        result = enable_guardduty_all_regions()
        
        # Should have results for both regions
        self.assertEqual(len(result), 2)
        self.assertIn('us-east-1', result)
        self.assertIn('eu-west-1', result)


class TestRegionErrorHandling(unittest.TestCase):
    """Test error handling in region operations."""

    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_ec2 = MagicMock()
        self.mock_session.client.return_value = self.mock_ec2

    def test_get_enabled_regions_client_error(self):
        """Test handling of client errors."""
        from botocore.exceptions import ClientError
        
        self.mock_ec2.describe_regions.side_effect = ClientError(
            error_response={'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            operation_name='DescribeRegions'
        )
        
        with self.assertRaises(ClientError):
            get_enabled_regions(self.mock_session)

    def test_get_enabled_regions_malformed_response(self):
        """Test handling of malformed API responses."""
        # Missing 'Regions' key
        self.mock_ec2.describe_regions.return_value = {}
        
        with self.assertRaises(KeyError):
            get_enabled_regions(self.mock_session)


@mock_aws
class TestRegionMotoIntegration(unittest.TestCase):
    """Integration tests using moto for real AWS API simulation."""
    
    def test_region_discovery_with_moto(self):
        """Test region discovery using moto's mock EC2."""
        session = boto3.Session(region_name='us-east-1')
        
        # This should work with moto's mock
        result = get_enabled_regions(session)
        
        # Moto should return some regions
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        
        # us-east-1 should always be included
        self.assertIn('us-east-1', result)


if __name__ == '__main__':
    unittest.main()