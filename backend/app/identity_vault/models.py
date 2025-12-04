"""
MongoDB Models for Identity Vault
Defines data structures for Users and Identity Logs
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles in the system - Power Rangers themed"""
    ADMIN = "admin"          # 🔴 Red Ranger - Full access
    OPERATOR = "operator"    # 🔵 Blue Ranger - Operational access
    VIEWER = "viewer"        # 🟡 Yellow Ranger - Read-only access


class UserInDB(BaseModel):
    """User model stored in MongoDB"""
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=100)
    hashed_password: str
    role: UserRole
    qr_token: str = Field(..., description="Unique QR token for authentication")
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "blue_ranger_001",
                "full_name": "Billy Cranston",
                "role": "operator",
                "qr_token": "abc123def456...",
                "is_active": True
            }
        }


class IdentityLog(BaseModel):
    """Identity log model for tracking authentication events"""
    username: str
    action: str = Field(..., description="Action performed (login, logout, failed_login)")
    success: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "blue_ranger_001",
                "action": "login",
                "success": True,
                "ip_address": "192.168.1.100",
                "timestamp": "2024-01-15T10:30:00"
            }
        }