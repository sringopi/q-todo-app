"""
IP filtering middleware for the TODO API.
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable

from app.core.config import settings


class IPFilterMiddleware(BaseHTTPMiddleware):
    """Middleware to filter requests based on IP allowlist."""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Filter requests based on IP allowlist."""
        
        # Skip IP filtering if disabled or no allowlist configured
        if not self.enabled or not settings.allowed_ips:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if IP is in allowlist
        if client_ip not in settings.allowed_ips:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied for IP: {client_ip}"
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
