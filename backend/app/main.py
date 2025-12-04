"""
SentinelOps-Nexus Backend - Phase 1
FastAPI Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.identity_vault.routes import router as identity_router
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await connect_to_mongo()
    print("🚀 SentinelOps-Nexus Backend Online!")
    print(f"⚡ Morphin Grid Status: ACTIVE")
    print(f"🔵 MongoDB Connected: {settings.MONGODB_URL}")
    yield
    # Shutdown
    await close_mongo_connection()
    print("🔴 Power Down Complete")


# Initialize FastAPI app
app = FastAPI(
    title="SentinelOps-Nexus API",
    description="Phase 1: Identity Vault & Authentication System - Power Rangers Edition",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(identity_router, prefix="/api/v1", tags=["Identity Vault"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "🔥 It's Morphin Time! SentinelOps-Nexus API is ready!",
        "phase": "1 - Identity Vault",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "morphin_grid": "active",
        "command_center": "operational",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )