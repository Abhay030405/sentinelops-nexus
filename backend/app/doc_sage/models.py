"""
DocSage Data Models
Pydantic models for request/response validation and MongoDB schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}


class PageSummary(BaseModel):
    """Individual page summary"""
    page_number: int = Field(..., description="Page number")
    text_content: str = Field(..., description="Text content of the page")
    summary: Optional[str] = Field(None, description="AI summary of the page")
    key_points: List[str] = Field(default_factory=list, description="Key points extracted")


class DocumentSummary(BaseModel):
    """Document summary information"""
    short_summary: Optional[str] = Field(None, description="Brief summary")
    long_summary: Optional[str] = Field(None, description="Detailed summary")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    tag_suggestions: List[str] = Field(default_factory=list, description="AI-suggested tags")
    page_summaries: List[PageSummary] = Field(default_factory=list, description="Page-level summaries")


class DocumentInsights(BaseModel):
    """AI-powered document insights"""
    total_pages: int = Field(0, description="Total number of pages")
    word_count: int = Field(0, description="Total word count")
    estimated_read_time: int = Field(0, description="Estimated read time in minutes")
    document_type: Optional[str] = Field(None, description="Detected document type")
    key_entities: List[str] = Field(default_factory=list, description="Key entities detected")
    important_sections: List[str] = Field(default_factory=list, description="Important sections")


class DocumentUploadResponse(BaseModel):
    """Response when document is uploaded"""
    id: str = Field(..., description="Document ID")
    name: str = Field(..., description="File name")
    status: str = Field(default="processing")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: str = Field(default="Current Ranger")
    mission_id: Optional[str] = Field(None, description="Associated mission ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Zord_Repair_Manual.pdf",
                "status": "processing",
                "uploaded_at": "2024-01-15T10:30:00",
                "uploaded_by": "Blue Ranger"
            }
        }


class DocumentDetail(BaseModel):
    """Complete document details"""
    id: str = Field(..., description="Document ID")
    name: str = Field(..., description="File name")
    status: str = Field(..., description="Processing status")
    uploaded_by: str = Field(..., description="Who uploaded")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    extracted_text: Optional[str] = Field(None, description="Extracted text")
    summary: Optional[DocumentSummary] = Field(None, description="AI summary")
    insights: Optional[DocumentInsights] = Field(None, description="AI-powered insights")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="File MIME type")
    mission_id: Optional[str] = Field(None, description="Associated mission ID")
    allowed_users: List[str] = Field(default_factory=list, description="Users with access")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Zord_Repair_Manual.pdf",
                "status": "processed",
                "uploaded_by": "Blue Ranger",
                "uploaded_at": "2024-01-15T10:30:00",
                "extracted_text": "This is extracted text...",
                "summary": {
                    "short_summary": "Guide for Zord maintenance",
                    "long_summary": "Comprehensive guide...",
                    "keywords": ["zord", "maintenance"]
                },
                "file_size": 2048576,
                "mime_type": "application/pdf"
            }
        }


class SearchResult(BaseModel):
    """Search result item"""
    id: str
    name: str
    summary: Optional[str]
    keywords: List[str]
    uploaded_by: str
    uploaded_at: datetime
    match_context: Optional[str] = Field(None, description="Matched text context")


class SearchResponse(BaseModel):
    """Search API response"""
    query: str = Field(..., description="Search query")
    total_results: int = Field(..., description="Total results")
    results: List[SearchResult] = Field(..., description="Results")


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    status_code: int


class ChatMessage(BaseModel):
    """Chat message in document chat"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatHistory(BaseModel):
    """Chat history for a document"""
    document_id: str = Field(..., description="Document ID")
    mission_id: Optional[str] = Field(None, description="Mission ID")
    user_id: str = Field(..., description="User ID")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Chat request from user"""
    document_id: str = Field(..., description="Document ID to chat about")
    question: str = Field(..., description="User's question")
    include_history: bool = Field(default=True, description="Include chat history")


class ChatResponse(BaseModel):
    """Chat response"""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[str] = Field(default_factory=list, description="Source references")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DocumentAccessRequest(BaseModel):
    """Request to access a document"""
    document_id: str = Field(..., description="Document ID")
    user_email: str = Field(..., description="User email requesting access")


class DocumentAccessResponse(BaseModel):
    """Response for document access"""
    has_access: bool = Field(..., description="Whether user has access")
    reason: Optional[str] = Field(None, description="Reason for access/denial")