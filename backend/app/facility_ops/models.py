"""
Facility Ops Hub Models
Issue Tracking System for HQ Maintenance
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class IssuePriority(str, Enum):
    """Issue priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueStatus(str, Enum):
    """Issue status workflow"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class IssueOutcome(str, Enum):
    """Outcome when technician completes work"""
    SUCCESS = "success"
    FAILED = "failed"


class IssueCategory(str, Enum):
    """Issue categories"""
    CCTV = "cctv"
    DOOR_ACCESS = "door_access"
    COMPUTER = "computer"
    POWER_SUPPLY = "power_supply"
    NETWORK = "network"
    OTHER = "other"


class ActivityLog(BaseModel):
    """Activity log entry for issue tracking"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str = Field(..., description="Action performed")
    performed_by: str = Field(..., description="User ID who performed action")
    performed_by_name: str = Field(..., description="User name")
    details: Optional[str] = Field(None, description="Additional details")


class IssueCreate(BaseModel):
    """Model for creating a new issue"""
    title: str = Field(..., min_length=3, max_length=200, description="Issue title")
    description: str = Field(..., min_length=10, description="Detailed description")
    priority: IssuePriority = Field(..., description="Priority level")
    category: IssueCategory = Field(default=IssueCategory.OTHER, description="Issue category")
    location: Optional[str] = Field(None, description="Building/Floor/Room location")


class IssueUpdate(BaseModel):
    """Model for updating issue details"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    priority: Optional[IssuePriority] = None
    category: Optional[IssueCategory] = None
    location: Optional[str] = None


class IssueAssign(BaseModel):
    """Model for assigning issue to technician"""
    technician_id: str = Field(..., description="Technician user ID to assign")
    notes: Optional[str] = Field(None, description="Assignment notes from admin")


class IssueOutcomeSubmit(BaseModel):
    """Model for technician to submit work outcome"""
    outcome: IssueOutcome = Field(..., description="Success or Failed")
    notes: str = Field(..., min_length=10, description="Work completion notes")
    resolution_details: Optional[str] = Field(None, description="How the issue was resolved")


class IssueStatusUpdate(BaseModel):
    """Model for admin to update issue status"""
    status: IssueStatus = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Status change notes")


class AISuggestion(BaseModel):
    """AI-generated suggestions for issue resolution"""
    suggestion: str = Field(..., description="Suggested solution")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class IssueResponse(BaseModel):
    """Complete issue response model"""
    id: str = Field(..., alias="_id")
    issue_number: int = Field(..., description="Sequential issue number")
    title: str
    description: str
    priority: IssuePriority
    category: IssueCategory
    location: Optional[str]
    status: IssueStatus
    
    # User tracking
    created_by: str = Field(..., description="User ID who created the issue")
    created_by_name: str = Field(..., description="Name of user who created")
    created_by_role: str = Field(..., description="Role of creator (admin/agent)")
    created_at: datetime
    updated_at: datetime
    
    # Assignment tracking
    assigned_to: Optional[str] = Field(None, description="Technician ID")
    assigned_to_name: Optional[str] = Field(None, description="Technician name")
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[str] = Field(None, description="Admin who assigned")
    
    # Completion tracking
    completed_at: Optional[datetime] = None
    outcome: Optional[IssueOutcome] = None
    resolution_notes: Optional[str] = None
    
    # Activity and AI
    activity_log: List[ActivityLog] = Field(default_factory=list)
    ai_suggestions: List[AISuggestion] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True
        # Ensure the model serializes using field names, not aliases
        from_attributes = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "issue_number": 123,
                "title": "CCTV Camera not working",
                "description": "Camera 14 in Building B is offline",
                "priority": "high",
                "category": "cctv",
                "location": "Building B, Floor 2",
                "status": "pending",
                "created_by": "user_id",
                "created_by_name": "Ranger Smith",
                "created_by_role": "agent",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }


class TechnicianScoreUpdate(BaseModel):
    """Model for updating technician score"""
    score_change: int = Field(..., description="Score change (+50 for success, -25 for failure)")
    reason: str = Field(..., description="Reason for score change")
