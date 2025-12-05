"""
DocSage API Routes
Endpoints for document upload, processing, and search
"""

import logging
import os
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from bson import ObjectId
from app.config.settings import settings
from app.doc_sage.models import (
    DocumentUploadResponse, 
    DocumentDetail, 
    SearchResponse,
    SearchResult,
    ErrorResponse
)
from app.doc_sage.services import document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["Documents"])


def _ensure_upload_dir():
    """Ensure upload directory exists"""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/documents", exist_ok=True)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    summary="Upload a document",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file"},
        413: {"model": ErrorResponse, "description": "File too large"},
    }
)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for processing.
    
    Supported formats:
    - PDF (.pdf)
    - Images (.jpg, .jpeg, .png)
    - Text (.txt)
    
    Returns document ID and processing status
    """
    try:
        logger.info(f"📤 Uploading file: {file.filename}")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed"
            )
        
        contents = await file.read()
        if len(contents) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds {settings.MAX_FILE_SIZE / 1024 / 1024}MB limit"
            )
        
        mime_type_map = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        mime_type = mime_type_map.get(file_ext, "application/octet-stream")
        
        _ensure_upload_dir()
        file_path = f"{settings.UPLOAD_DIR}/documents/{file.filename}"
        
        counter = 1
        while os.path.exists(file_path):
            name, ext = os.path.splitext(file.filename)
            file_path = f"{settings.UPLOAD_DIR}/documents/{name}_{counter}{ext}"
            counter += 1
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"✅ File saved: {file_path}")
        
        doc = await document_service.create_document(
            filename=os.path.basename(file_path),
            file_path=file_path,
            file_size=len(contents),
            mime_type=mime_type
        )
        
        asyncio.create_task(
            document_service.process_document_text(doc["_id"])
        )
        
        return DocumentUploadResponse(
            id=doc["_id"],
            name=doc["name"],
            status=doc["status"],
            uploaded_at=doc["uploaded_at"],
            uploaded_by=doc["uploaded_by"]
        )
    
    except HTTPException as e:
        logger.error(f"❌ Upload error: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Error during upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{doc_id}/summary",
    response_model=DocumentDetail,
    summary="Get document summary"
)
async def get_document_summary(doc_id: str):
    """
    Get document with summary, keywords, and extracted text.
    
    Returns full document details including AI-generated summary.
    """
    try:
        logger.info(f"📖 Getting document: {doc_id}")
        
        # Validate ObjectId format
        if not ObjectId.is_valid(doc_id):
            raise HTTPException(status_code=400, detail="Invalid document ID format")
        
        doc = await document_service.get_document(doc_id)
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentDetail(
            id=doc["_id"],
            name=doc["name"],
            status=doc["status"],
            uploaded_by=doc["uploaded_by"],
            uploaded_at=doc["uploaded_at"],
            extracted_text=doc.get("extracted_text"),
            summary=doc.get("summary"),
            file_size=doc["file_size"],
            mime_type=doc["mime_type"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/search",
    response_model=SearchResponse,
    summary="Search documents"
)
async def search_documents(q: str = Query(..., min_length=1, max_length=100)):
    """
    Search documents by content and keywords.
    
    Searches across document names, extracted text, keywords, and summaries.
    """
    try:
        logger.info(f"🔍 Searching for: {q}")
        
        results = await document_service.search_documents(q)
        
        formatted_results = []
        for doc in results:
            match_context = None
            if doc.get("extracted_text"):
                text = doc["extracted_text"]
                idx = text.lower().find(q.lower())
                if idx != -1:
                    start = max(0, idx - 50)
                    end = min(len(text), idx + len(q) + 50)
                    match_context = f"...{text[start:end]}..."
            
            formatted_results.append(
                SearchResult(
                    id=doc["_id"],
                    name=doc["name"],
                    summary=doc.get("summary", {}).get("short_summary"),
                    keywords=doc.get("summary", {}).get("keywords", []),
                    uploaded_by=doc["uploaded_by"],
                    uploaded_at=doc["uploaded_at"],
                    match_context=match_context
                )
            )
        
        return SearchResponse(
            query=q,
            total_results=len(formatted_results),
            results=formatted_results
        )
    
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "",
    response_model=list[DocumentDetail],
    summary="Get all documents"
)
async def get_all_documents():
    """
    Get all documents with their summaries and processing status.
    
    Returns all documents sorted by upload date (newest first).
    """
    try:
        logger.info("📚 Getting all documents")
        
        docs = await document_service.get_all_documents()
        
        return [
            DocumentDetail(
                id=doc["_id"],
                name=doc["name"],
                status=doc["status"],
                uploaded_by=doc["uploaded_by"],
                uploaded_at=doc["uploaded_at"],
                extracted_text=doc.get("extracted_text"),
                summary=doc.get("summary"),
                file_size=doc["file_size"],
                mime_type=doc["mime_type"]
            )
            for doc in docs
        ]
    
    except Exception as e:
        logger.error(f"❌ Error getting documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{doc_id}",
    summary="Delete document"
)
async def delete_document(doc_id: str):
    """
    Delete a document and its associated file.
    
    Removes document from database and deletes the stored file.
    """
    try:
        logger.info(f"🗑️ Deleting document: {doc_id}")
        
        # Validate ObjectId format
        if not ObjectId.is_valid(doc_id):
            raise HTTPException(status_code=400, detail="Invalid document ID format")
        
        success = await document_service.delete_document(doc_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully", "id": doc_id}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
