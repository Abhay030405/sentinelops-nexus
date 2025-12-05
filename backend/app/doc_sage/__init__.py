"""
Doc-Sage Module
Document processing and AI-powered intelligence system
"""

from app.doc_sage.routes import router
from app.doc_sage.services import document_service
from app.doc_sage.ai_processor import get_ai_processor

__all__ = ["router", "document_service", "get_ai_processor"]
