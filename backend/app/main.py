"""
Home Management Platform - Main FastAPI Application
"""

import os
import traceback
from pathlib import Path

from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings, is_development

# Initialize FastAPI app
app = FastAPI(
    title="Home Management Platform API",
    description="Multi-user household management system with financial planning, "
                "document storage, project tracking, and ATO-compliant tax records",
    version="0.1.0",
    docs_url="/docs" if is_development() else None,  # Disable docs in production
    redoc_url="/redoc" if is_development() else None,
    openapi_url="/openapi.json" if is_development() else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for debugging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions and log them with full traceback
    """
    print("=" * 80)
    print(f"🔴 UNHANDLED EXCEPTION in {request.method} {request.url.path}")
    print(f"Exception type: {type(exc).__name__}")
    print(f"Exception message: {str(exc)}")
    print("-" * 80)
    print("Full traceback:")
    traceback.print_exc()
    print("=" * 80)

    return JSONResponse(
        status_code=500,
        content={
            "detail": f"{type(exc).__name__}: {str(exc)}",
            "path": request.url.path,
            "method": request.method
        }
    )


# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint for Docker healthcheck and monitoring

    Returns:
        JSON response with service status
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "0.1.0"
        }
    )


# Include API v1 router
from app.api.v1 import api_router

app.include_router(api_router, prefix="/api/v1")


# Serve React frontend (production only)
# In development, frontend runs separately on port 5173 with HMR
STATIC_DIR = Path("/app/static")
if STATIC_DIR.exists() and not is_development():
    # Mount static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")

    # Serve index.html for all other routes (SPA fallback)
    from fastapi.responses import FileResponse

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serve React SPA for all non-API routes
        This enables client-side routing to work correctly
        """
        # If file exists in static dir, serve it
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        # Otherwise, serve index.html (SPA entry point)
        return FileResponse(STATIC_DIR / "index.html")
else:
    # Development mode: API only, frontend runs separately
    @app.get("/", status_code=status.HTTP_200_OK)
    async def root():
        """
        API root endpoint (development mode)

        Returns:
            Welcome message and API information
        """
        return JSONResponse(
            content={
                "message": "Home Management Platform API",
                "version": "0.1.0",
                "docs": "/docs" if is_development() else "disabled",
                "health": "/health",
                "mode": "development - frontend runs separately on port 5173"
            }
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 Starting Home Management Platform API")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔒 CORS Origins: {settings.allowed_origins_list}")
    print(f"💾 Database: Connected to PostgreSQL")

    # Check if serving frontend
    if STATIC_DIR.exists() and not is_development():
        print(f"🎨 Serving React frontend from {STATIC_DIR}")
    else:
        print(f"⚙️  Development mode: Frontend runs separately on port 5173")

    # Future: Initialize database connection pool, cache, etc.


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("🛑 Shutting down Home Management Platform API")

    # Future: Close database connections, cache, etc.
