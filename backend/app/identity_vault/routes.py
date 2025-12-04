"""
Identity Vault API Routes
Phase 1 Endpoints: User creation, authentication, validation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from datetime import datetime
from typing import List

from app.identity_vault.schemas import (
    UserCreate, UserResponse, LoginRequest, LoginResponse,
    TokenValidationResponse, IdentityLogResponse
)
from app.identity_vault.utils import (
    generate_qr_token, hash_password, verify_password, generate_qr_code_image
)
from app.utils.auth import create_access_token
from app.utils.dependencies import get_current_active_user, require_admin
from app.database.mongodb import get_database

router = APIRouter()


@router.post("/admin/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: dict = Depends(require_admin),
    db = Depends(get_database)
):
    """
    🔴 RED RANGER ONLY: Create a new user
    
    Requires admin role to create new users in the system.
    Generates unique QR token for each user.
    """
    # Check if username already exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' already exists"
        )
    
    # Generate QR token
    qr_token = generate_qr_token()
    
    # Create user document
    user_doc = {
        "username": user_data.username,
        "full_name": user_data.full_name,
        "hashed_password": hash_password(user_data.password),
        "role": user_data.role,
        "qr_token": qr_token,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    # Insert into database
    result = await db.users.insert_one(user_doc)
    
    # Log the action
    await db.identity_logs.insert_one({
        "username": user_data.username,
        "action": "user_created",
        "success": True,
        "ip_address": request.client.host,
        "timestamp": datetime.utcnow(),
        "details": f"Created by {current_user['username']}"
    })
    
    # Return user response
    user_doc["_id"] = str(result.inserted_id)
    return UserResponse(**user_doc)


@router.post("/auth/scan", response_model=LoginResponse)
async def authenticate_user(
    login_data: LoginRequest,
    request: Request,
    db = Depends(get_database)
):
    """
    ⚡ MORPHIN TIME: Authenticate user with credentials
    
    Validates username and password, returns JWT token.
    Logs authentication attempt.
    """
    # Find user
    user = await db.users.find_one({"username": login_data.username})
    
    # Verify credentials
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        # Log failed attempt
        await db.identity_logs.insert_one({
            "username": login_data.username,
            "action": "login_failed",
            "success": False,
            "ip_address": request.client.host,
            "timestamp": datetime.utcnow(),
            "details": "Invalid credentials"
        })
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    await db.users.update_one(
        {"username": login_data.username},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    
    # Log successful login
    await db.identity_logs.insert_one({
        "username": login_data.username,
        "action": "login_success",
        "success": True,
        "ip_address": request.client.host,
        "timestamp": datetime.utcnow(),
        "details": "Authentication successful"
    })
    
    # Prepare user response
    user_response = UserResponse(
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"],
        qr_token=user["qr_token"],
        is_active=user["is_active"],
        created_at=user["created_at"],
        last_login=user.get("last_login")
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/auth/validate", response_model=TokenValidationResponse)
async def validate_token(
    current_user: dict = Depends(get_current_active_user)
):
    """
    ✅ Validate JWT Token
    
    Checks if the provided token is valid and returns user info.
    """
    user_response = UserResponse(
        username=current_user["username"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        qr_token=current_user["qr_token"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login")
    )
    
    return TokenValidationResponse(
        valid=True,
        user=user_response,
        message="Token is valid"
    )


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_active_user)
):
    """
    👤 Get Current User Profile
    
    Returns the authenticated user's profile information.
    """
    return UserResponse(
        username=current_user["username"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        qr_token=current_user["qr_token"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login")
    )


@router.get("/auth/logs", response_model=List[IdentityLogResponse])
async def get_identity_logs(
    limit: int = 50,
    current_user: dict = Depends(get_current_active_user),
    db = Depends(get_database)
):
    """
    📊 Get Identity Logs
    
    Returns recent authentication logs.
    Admins see all logs, others see only their own.
    """
    # Build query based on role
    if current_user["role"] == "admin":
        query = {}  # Admins see all logs
    else:
        query = {"username": current_user["username"]}  # Users see only their logs
    
    # Fetch logs
    cursor = db.identity_logs.find(query).sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    
    # Convert to response model
    return [IdentityLogResponse(**log) for log in logs]


@router.get("/admin/qr-code/{username}")
async def get_user_qr_code(
    username: str,
    current_user: dict = Depends(require_admin),
    db = Depends(get_database)
):
    """
    🔴 RED RANGER ONLY: Generate QR code for user
    
    Returns base64 encoded QR code image for user authentication.
    """
    user = await db.users.find_one({"username": username})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found"
        )
    
    # Generate QR code
    qr_data = f"SENTINEL_OPS::{user['username']}::{user['qr_token']}"
    qr_image = generate_qr_code_image(qr_data)
    
    return {
        "username": username,
        "qr_code": qr_image,
        "qr_token": user["qr_token"]
    }