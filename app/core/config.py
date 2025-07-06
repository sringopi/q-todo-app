"""
Application configuration settings.
"""
import ipaddress
from typing import List, Optional, Union
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "TODO API"
    version: str = "1.0.0"
    description: str = "A simple TODO API built with FastAPI"
    debug: bool = False
    
    # Security settings
    ip_allowlist: Optional[str] = None
    secret_key: Optional[str] = None
    
    # Database settings (for future use)
    database_url: Optional[str] = None
    
    # Redis settings (for future use)
    redis_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_ip_ranges(self) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
        """Parse IP allowlist into a list of IP networks (CIDR ranges)."""
        if not self.ip_allowlist:
            # Default to allow all traffic when no allowlist is configured
            return [ipaddress.IPv4Network('0.0.0.0/0'), ipaddress.IPv6Network('::/0')]
        
        networks = []
        for ip_range in self.ip_allowlist.split(","):
            ip_range = ip_range.strip()
            if not ip_range:
                continue
            
            try:
                # Handle single IP addresses by adding /32 (IPv4) or /128 (IPv6)
                if '/' not in ip_range:
                    # Determine if it's IPv4 or IPv6
                    try:
                        ip_obj = ipaddress.ip_address(ip_range)
                        if isinstance(ip_obj, ipaddress.IPv4Address):
                            ip_range += '/32'
                        else:
                            ip_range += '/128'
                    except ValueError:
                        continue
                
                # Parse as network
                network = ipaddress.ip_network(ip_range, strict=False)
                networks.append(network)
            except ValueError as e:
                # Log invalid IP ranges but continue processing others
                print(f"Warning: Invalid IP range '{ip_range}': {e}")
                continue
        
        # If no valid networks were parsed, default to allow all
        if not networks:
            return [ipaddress.IPv4Network('0.0.0.0/0'), ipaddress.IPv6Network('::/0')]
        
        return networks
    
    @property
    def allowed_ips(self) -> List[str]:
        """Parse IP allowlist into a list of IP addresses/ranges (for backward compatibility)."""
        if not self.ip_allowlist:
            return ['0.0.0.0/0', '::/0']
        return [ip.strip() for ip in self.ip_allowlist.split(",") if ip.strip()]
    
    def is_ip_allowed(self, client_ip: str) -> bool:
        """Check if a client IP is allowed based on the configured IP ranges."""
        if not self.ip_allowlist:
            # No allowlist configured - allow all traffic
            return True
        
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            
            # Check if client IP is in any of the allowed ranges
            for network in self.allowed_ip_ranges:
                if client_ip_obj in network:
                    return True
            
            return False
        except ValueError:
            # Invalid IP address format
            return False


settings = Settings()
