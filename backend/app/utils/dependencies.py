"""
FastAPI Dependencies
Authentication middleware and RBAC
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.utils.auth import decode_access_token
from app.database.mongodb import get_database
from app.identity_vault.models import UserRole

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token from request
        
    Returns:
        User document from database
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    username = payload.get("sub")
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    db = get_database()
    user = await db.users.find_one({"username": username})
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    
    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
):
    """
    Verify user is active
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Active user document
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def require_role(required_role: UserRole):
    """
    Factory function to create role-checking dependency
    
    Args:
        required_role: Minimum required role
        
    Returns:
        Dependency function
    """
    async def role_checker(current_user: dict = Depends(get_current_active_user)):
        user_role = current_user.get("role")
        
        # Role hierarchy: admin > operator > viewer
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.OPERATOR: 2,
            UserRole.VIEWER: 1
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return current_user
    
    return role_checker


async def require_admin(current_user: dict = Depends(get_current_active_user)):
    """
    Require admin role for endpoint access
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if admin, raises exception otherwise
    """
    if current_user.get("role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. You must be a Red Ranger!"
        )
    return current_user