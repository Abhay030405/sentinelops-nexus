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


class DocumentSummary(BaseModel):
    """Document summary information"""
    short_summary: Optional[str] = Field(None, description="Brief summary")
    long_summary: Optional[str] = Field(None, description="Detailed summary")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")


class DocumentUploadResponse(BaseModel):
    """Response when document is uploaded"""
    id: str = Field(..., description="Document ID")
    name: str = Field(..., description="File name")
    status: str = Field(default="processing")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: str = Field(default="Current Ranger")
    
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
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="File MIME type")
    
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
    upload_date: datetime
    file_type: str
    file_size: int
    short_summary: Optional[str] = None
    long_summary: Optional[str] = None
    keywords: List[str] = []
    
class DocumentSummaryResponse(BaseModel):
    id: str
    name: str
    status: str
    summary: Optional[str] = None
    keywords: List[str] = []
    extracted_text: Optional[str] = None