"""
Knowledge Crystal API Routes
Endpoints for KB creation, search, and Q&A
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase

from .models import (
    KBPageCreate, KBPageUpdate, KBPageResponse,
    SearchQuery, SearchResult, QueryRequest, QueryResponse
)
from .services import KBPageService, KBSearchService, KBRAGService
from app.utils.dependencies import get_db

router = APIRouter(prefix="/kb", tags=["knowledge-crystal"])


@router.post("/create", response_model=dict)
async def create_kb_page(
    page_data: KBPageCreate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Create a new knowledge page and generate embeddings
    
    STEP 1: Creates KB page in MongoDB
    STEP 2: Chunks content and generates embeddings with Gemini
    STEP 3: Stores chunks in vector DB (ChromaDB)
    """
    service = KBPageService(db)
    result = await service.create_page(page_data)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return {
        "message": "Knowledge page created successfully",
        "data": result
    }


@router.get("/page/{page_id}", response_model=dict)
async def get_kb_page(
    page_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve a knowledge page by ID"""
    service = KBPageService(db)
    page = await service.get_page(page_id)
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    
    return {
        "data": page
    }


@router.get("/pages", response_model=dict)
async def list_kb_pages(
    visibility: Optional[str] = Query(None, description="Filter by visibility (public/private)"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(10, ge=1, le=50),
    skip: int = Query(0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List knowledge pages with optional filters"""
    service = KBPageService(db)
    result = await service.list_pages(
        visibility=visibility,
        tags=tags,
        limit=limit,
        skip=skip
    )
    
    return result


@router.put("/page/{page_id}", response_model=dict)
async def update_kb_page(
    page_id: str,
    update_data: KBPageUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update a knowledge page (re-indexes if content changed)"""
    service = KBPageService(db)
    result = await service.update_page(page_id, update_data)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return {
        "message": "Page updated successfully",
        "data": result
    }


@router.delete("/page/{page_id}", response_model=dict)
async def delete_kb_page(
    page_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete a knowledge page and its chunks"""
    service = KBPageService(db)
    result = await service.delete_page(page_id)
    
    return {
        "message": "Page deleted successfully",
        "data": result
    }


@router.get("/search", response_model=dict)
async def semantic_search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20),
    tags: Optional[List[str]] = Query(None),
    visibility: Optional[str] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Perform semantic search on knowledge pages
    
    This is the smart search endpoint that uses vector similarity
    instead of keyword matching.
    """
    search_query = SearchQuery(
        query=q,
        limit=limit,
        tags=tags,
        visibility=visibility
    )
    
    service = KBSearchService(db)
    results = await service.search(search_query, limit=limit)
    
    return {
        "query": q,
        "results_count": len(results),
        "results": results
    }


@router.post("/query", response_model=dict)
async def kb_query(
    query_req: QueryRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Ask a question and get an AI-generated answer using RAG
    
    This endpoint:
    1. Converts question to embedding
    2. Retrieves relevant chunks from vector DB
    3. Uses Gemini LLM to synthesize answer from chunks
    4. Returns answer with source citations
    """
    service = KBRAGService(db)
    response = await service.query(query_req)
    
    return {
        "message": "Query processed successfully",
        "data": response
    }


@router.get("/stats", response_model=dict)
async def get_kb_stats(db: AsyncIOMotorDatabase = Depends(get_db)):
    """Get statistics about the knowledge base"""
    service = KBPageService(db)
    
    total_pages = await service.collection.count_documents({})
    public_pages = await service.collection.count_documents({"visibility": "public"})
    private_pages = await service.collection.count_documents({"visibility": "private"})
    
    # Get tags
    tags_result = await service.collection.aggregate([
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(length=20)
    
    return {
        "total_pages": total_pages,
        "public_pages": public_pages,
        "private_pages": private_pages,
        "top_tags": tags_result
    }


@router.get("/health", response_model=dict)
async def kb_health():
    """Health check for Knowledge Crystal service"""
    return {
        "status": "healthy",
        "service": "knowledge-crystal",
        "features": [
            "kb_page_creation",
            "vector_embeddings",
            "semantic_search",
            "rag_qa_engine"
        ]
    }
