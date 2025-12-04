"""
Pydantic Schemas for Request/Response validation
Defines API input/output structures
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.identity_vault.models import UserRole


# Request Schemas
class UserCreate(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.OPERATOR
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "pink_ranger_001",
                "password": "secure_password_123",
                "full_name": "Kimberly Hart",
                "role": "operator"
            }
        }


class LoginRequest(BaseModel):
    """Schema for login/authentication"""
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "blue_ranger_001",
                "password": "my_secure_password"
            }
        }


class TokenValidation(BaseModel):
    """Schema for token validation request"""
    token: str


# Response Schemas
class UserResponse(BaseModel):
    """Schema for user data in responses"""
    username: str
    full_name: str
    role: str
    qr_token: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "blue_ranger_001",
                "full_name": "Billy Cranston",
                "role": "operator",
                "qr_token": "abc123def456ghi789...",
                "is_active": True,
                "created_at": "2024-01-15T10:00:00",
                "last_login": "2024-01-15T14:30:00"
            }
        }


class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "username": "blue_ranger_001",
                    "full_name": "Billy Cranston",
                    "role": "operator"
                }
            }
        }


class TokenValidationResponse(BaseModel):
    """Schema for token validation response"""
    valid: bool
    user: Optional[UserResponse] = None
    message: str


class IdentityLogResponse(BaseModel):
    """Schema for identity log entries"""
    username: str
    action: str
    success: bool
    ip_address: Optional[str] = None
    timestamp: datetime
    details: Optional[str] = None