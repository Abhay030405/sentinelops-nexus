from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class KBPageCreate(BaseModel):
    """Schema for creating a knowledge page"""
    title: str = Field(..., min_length=1, max_length=255, description="Page title")
    content: str = Field(..., min_length=1, description="Page content")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    visibility: str = Field(default="public", description="public or private")
    author: Optional[str] = Field(default="system", description="Author of the page")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")


class KBPageUpdate(BaseModel):
    """Schema for updating a knowledge page"""
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    visibility: Optional[str] = None
    metadata: Optional[dict] = None


class KBPageResponse(BaseModel):
    """Schema for knowledge page response"""
    id: str = Field(..., description="Page ID (MongoDB ObjectId)")
    title: str
    content: str
    tags: List[str]
    visibility: str
    author: str
    created_at: datetime
    updated_at: datetime
    chunk_count: int = Field(default=0, description="Number of chunks created")
    status: str = Field(default="indexed", description="Status: indexed, indexing, error")
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class KBChunk(BaseModel):
    """Schema for a chunk of content (for vector storage)"""
    id: str = Field(..., description="Unique chunk ID")
    page_id: str = Field(..., description="Parent page ID")
    content: str = Field(..., description="Chunk text content")
    chunk_index: int = Field(..., description="Order of chunk in page")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SearchQuery(BaseModel):
    """Schema for search queries"""
    query: str = Field(..., min_length=1, description="Search query text")
    limit: int = Field(default=5, ge=1, le=20, description="Max results to return")
    tags: Optional[List[str]] = None
    visibility: Optional[str] = None


class SearchResult(BaseModel):
    """Schema for search results"""
    page_id: str
    title: str
    content: str
    tags: List[str]
    chunk_snippet: str = Field(..., description="Relevant chunk from the page")
    similarity_score: float = Field(..., ge=0, le=1, description="Similarity score (0-1)")
    author: str


class QueryRequest(BaseModel):
    """Schema for Q&A queries"""
    question: str = Field(..., min_length=5, description="Question to ask")
    limit: int = Field(default=5, ge=1, le=20, description="Max context chunks to retrieve")
    visibility: Optional[str] = None
    tags: Optional[List[str]] = None


class QueryResponse(BaseModel):
    """Schema for Q&A response"""
    answer: str = Field(..., description="AI-generated answer")
    sources: List[SearchResult] = Field(..., description="Source documents used")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level of answer")
    model_used: str = Field(default="gemini-2.0-flash", description="Model used for generation")
