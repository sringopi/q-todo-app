"""
Main FastAPI application.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.routers import todos
from app.middleware.ip_filter import IPFilterMiddleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=settings.description,
        debug=settings.debug,
    )
    
    # Add IP filtering middleware (optional - can be enabled/disabled)
    # Uncomment the next line to enable IP filtering
    # app.add_middleware(IPFilterMiddleware, enabled=bool(settings.allowed_ips))
    
    # Include routers
    app.include_router(todos.router, prefix="/api/v1")
    
    # Custom exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        # Convert errors to JSON serializable format
        errors = []
        for error in exc.errors():
            error_dict = {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "input": error.get("input")
            }
            # Handle ValueError context
            if "ctx" in error and "error" in error["ctx"]:
                error_dict["ctx"] = {"error": str(error["ctx"]["error"])}
            errors.append(error_dict)
        
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": errors
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy", 
            "version": settings.version,
            "ip_filtering": "enabled" if settings.allowed_ips else "disabled"
        }
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.version,
            "docs_url": "/docs",
            "health_url": "/health",
            "environment": "development" if settings.debug else "production"
        }
    
    # Configuration info endpoint (for debugging)
    @app.get("/config", tags=["debug"])
    async def config_info():
        """Configuration information endpoint (for debugging)."""
        if not settings.debug:
            return {"detail": "Configuration info only available in debug mode"}
        
        return {
            "app_name": settings.app_name,
            "version": settings.version,
            "debug": settings.debug,
            "ip_allowlist_configured": bool(settings.ip_allowlist),
            "ip_allowlist_raw": settings.ip_allowlist,
            "allowed_ip_ranges": [str(network) for network in settings.allowed_ip_ranges],
            "allowed_ranges_count": len(settings.allowed_ip_ranges),
            "default_behavior": "allow_all" if not settings.ip_allowlist else "restricted"
        }
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
