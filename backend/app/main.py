from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.doc_sage.routes import router as doc_sage_router
from app.knowledge_crystal.routes import router as kb_router
from app.knowledge_crystal.embedding_service import init_embedding_service
from app.knowledge_crystal.vector_store import init_vector_store

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Power Rangers Sentinel"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Doc-Sage Intel Console...")
    await connect_to_mongo()
    print("✅ MongoDB connected!")
    
    # Initialize Knowledge Crystal services
    print("🔮 Initializing Knowledge Crystal...")
    try:
        init_embedding_service()
        print("✅ Embedding Service initialized")
        
        init_vector_store()
        print("✅ Vector Store initialized")
    except Exception as e:
        print(f"⚠️ Knowledge Crystal initialization warning: {e}")
    
    print("✅ Doc-Sage & Knowledge Crystal are ready!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Include routers
app.include_router(doc_sage_router)
app.include_router(kb_router)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "🎯 Doc-Sage Intel Console API",
        "status": "online",
        "version": settings.APP_VERSION
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "doc-sage"}