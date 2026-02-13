"""
Home Management Platform - Main FastAPI Application
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    """
    API root endpoint

    Returns:
        Welcome message and API information
    """
    return JSONResponse(
        content={
            "message": "Home Management Platform API",
            "version": "0.1.0",
            "docs": "/docs" if is_development() else "disabled",
            "health": "/health"
        }
    )


# Include API v1 router
from app.api.v1 import api_router

app.include_router(api_router, prefix="/api/v1")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 Starting Home Management Platform API")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔒 CORS Origins: {settings.allowed_origins_list}")
    print(f"💾 Database: Connected to PostgreSQL")

    # Future: Initialize database connection pool, cache, etc.


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("🛑 Shutting down Home Management Platform API")

    # Future: Close database connections, cache, etc.
