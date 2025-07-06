"""
IP filtering middleware for the TODO API with CIDR range support.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable

from app.core.config import settings


class IPFilterMiddleware(BaseHTTPMiddleware):
    """Middleware to filter requests based on IP allowlist with CIDR range support."""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Filter requests based on IP allowlist with CIDR ranges."""
        
        # Skip IP filtering if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if IP is allowed using the enhanced CIDR-aware method
        if not settings.is_ip_allowed(client_ip):
            # Get allowed ranges for error message
            allowed_ranges = [str(network) for network in settings.allowed_ip_ranges]
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Access denied",
                    "client_ip": client_ip,
                    "allowed_ranges": allowed_ranges,
                    "message": f"IP {client_ip} is not in the allowed ranges"
                }
            )
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers."""
        # Check for forwarded headers (common in load balancers/proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
