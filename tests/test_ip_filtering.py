"""
Tests for IP filtering functionality with CIDR range support.
"""
import pytest
from unittest.mock import patch
from app.core.config import Settings


class TestIPFiltering:
    """Test IP filtering with CIDR ranges."""
    
    def test_no_allowlist_allows_all(self):
        """Test that no allowlist configuration allows all traffic."""
        settings = Settings(ip_allowlist=None)
        
        # Should allow any IP when no allowlist is configured
        assert settings.is_ip_allowed("192.168.1.1") is True
        assert settings.is_ip_allowed("10.0.0.1") is True
        assert settings.is_ip_allowed("203.0.113.1") is True
        assert settings.is_ip_allowed("::1") is True
    
    def test_empty_allowlist_allows_all(self):
        """Test that empty allowlist allows all traffic."""
        settings = Settings(ip_allowlist="")
        
        # Should allow any IP when allowlist is empty
        assert settings.is_ip_allowed("192.168.1.1") is True
        assert settings.is_ip_allowed("10.0.0.1") is True
    
    def test_single_ip_allowlist(self):
        """Test single IP address in allowlist."""
        settings = Settings(ip_allowlist="192.168.1.100")
        
        # Should allow the specific IP
        assert settings.is_ip_allowed("192.168.1.100") is True
        
        # Should deny other IPs
        assert settings.is_ip_allowed("192.168.1.101") is False
        assert settings.is_ip_allowed("10.0.0.1") is False
    
    def test_multiple_ips_allowlist(self):
        """Test multiple IP addresses in allowlist."""
        settings = Settings(ip_allowlist="192.168.1.100,10.0.0.50,203.0.113.1")
        
        # Should allow all listed IPs
        assert settings.is_ip_allowed("192.168.1.100") is True
        assert settings.is_ip_allowed("10.0.0.50") is True
        assert settings.is_ip_allowed("203.0.113.1") is True
        
        # Should deny unlisted IPs
        assert settings.is_ip_allowed("192.168.1.101") is False
        assert settings.is_ip_allowed("10.0.0.51") is False
    
    def test_cidr_range_allowlist(self):
        """Test CIDR range in allowlist."""
        settings = Settings(ip_allowlist="192.168.1.0/24")
        
        # Should allow IPs in the range
        assert settings.is_ip_allowed("192.168.1.1") is True
        assert settings.is_ip_allowed("192.168.1.100") is True
        assert settings.is_ip_allowed("192.168.1.254") is True
        
        # Should deny IPs outside the range
        assert settings.is_ip_allowed("192.168.2.1") is False
        assert settings.is_ip_allowed("10.0.0.1") is False
    
    def test_mixed_ips_and_cidr_ranges(self):
        """Test mix of individual IPs and CIDR ranges."""
        settings = Settings(ip_allowlist="192.168.1.0/24,10.0.0.50,203.0.113.0/28")
        
        # Should allow IPs in CIDR ranges
        assert settings.is_ip_allowed("192.168.1.100") is True
        assert settings.is_ip_allowed("203.0.113.5") is True
        
        # Should allow individual IP
        assert settings.is_ip_allowed("10.0.0.50") is True
        
        # Should deny IPs outside ranges
        assert settings.is_ip_allowed("192.168.2.1") is False
        assert settings.is_ip_allowed("10.0.0.51") is False
        assert settings.is_ip_allowed("203.0.113.20") is False
    
    def test_ipv6_support(self):
        """Test IPv6 address support."""
        settings = Settings(ip_allowlist="2001:db8::/32,::1")
        
        # Should allow IPv6 addresses in range
        assert settings.is_ip_allowed("2001:db8::1") is True
        assert settings.is_ip_allowed("::1") is True
        
        # Should deny IPv6 addresses outside range
        assert settings.is_ip_allowed("2001:db9::1") is False
    
    def test_invalid_ip_ranges_ignored(self):
        """Test that invalid IP ranges are ignored."""
        settings = Settings(ip_allowlist="192.168.1.100,invalid-ip,10.0.0.0/24")
        
        # Should still work with valid ranges
        assert settings.is_ip_allowed("192.168.1.100") is True
        assert settings.is_ip_allowed("10.0.0.50") is True
        
        # Should deny other IPs
        assert settings.is_ip_allowed("203.0.113.1") is False
    
    def test_auto_cidr_conversion(self):
        """Test that single IPs are auto-converted to /32."""
        settings = Settings(ip_allowlist="192.168.1.100")
        
        # Check that it's converted to a /32 network
        ranges = settings.allowed_ip_ranges
        assert len(ranges) == 1
        assert str(ranges[0]) == "192.168.1.100/32"
    
    def test_default_ranges_when_no_config(self):
        """Test default ranges when no configuration is provided."""
        settings = Settings(ip_allowlist=None)
        
        # Should default to allow all IPv4 and IPv6
        ranges = settings.allowed_ip_ranges
        range_strings = [str(r) for r in ranges]
        assert "0.0.0.0/0" in range_strings
        assert "::/0" in range_strings
    
    def test_whitespace_handling(self):
        """Test that whitespace in IP list is handled correctly."""
        settings = Settings(ip_allowlist=" 192.168.1.100 , 10.0.0.0/24 , 203.0.113.1 ")
        
        # Should work despite whitespace
        assert settings.is_ip_allowed("192.168.1.100") is True
        assert settings.is_ip_allowed("10.0.0.50") is True
        assert settings.is_ip_allowed("203.0.113.1") is True
    
    def test_invalid_client_ip_denied(self):
        """Test that invalid client IP format is denied."""
        settings = Settings(ip_allowlist="192.168.1.0/24")
        
        # Should deny invalid IP format
        assert settings.is_ip_allowed("invalid-ip") is False
        assert settings.is_ip_allowed("") is False
