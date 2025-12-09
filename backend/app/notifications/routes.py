"""
Notifications Routes
Phase 4 API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.notifications.models import (
    Notification, NotificationPreference, NotificationStats,
    NotificationType, NotificationPriority, NotificationChannel
)
from app.notifications.services import NotificationService
from app.utils.auth import verify_token
from app.database.mongodb import get_database
from typing import List, Optional

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


async def get_notification_service(db=Depends(get_database)) -> NotificationService:
    """Dependency to get notification service"""
    return NotificationService(db)


@router.get("/", response_model=dict)
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    notification_type: Optional[str] = None,
    is_read: Optional[bool] = None,
    user_id: str = Depends(verify_token),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Get user's notifications"""
    try:
        notif_type = NotificationType[notification_type.upper()] if notification_type else None
        
        notifications, total = await notification_service.get_notifications(
            user_id=user_id,
            limit=limit,
            offset=offset,
            notification_type=notif_type,
            is_read=is_read
        )
        
        return {
            "notifications": notifications,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )


@router.post("/{notification_id}/read", response_model=dict)
async def mark_notification_read(
    notification_id: str,
    user_id: str = Depends(verify_token),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Mark notification as read"""
    try:
        success = await notification_service.mark_as_read(user_id, notification_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark as read: {str(e)}"
        )


@router.post("/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    user_id: str = Depends(verify_token),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Mark all notifications as read"""
    try:
        count = await notification_service.mark_all_as_read(user_id)
        
        return {
            "message": f"{count} notifications marked as read",
            "count": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark as read: {str(e)}"
        )


@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: str,
    user_id: str = Depends(verify_token),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Delete notification"""
    try:
        success = await notification_service.delete_notification(user_id, notification_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete: {str(e)}"
        )


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    user_id: str = Depends(verify_token),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Get notification statistics"""
    try:
        stats = await notification_service.get_notification_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/preferences", response_model=NotificationPreference)
async def get_notification_preferences(
    user_id: str = Depends(verify_token),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Get notification preferences"""
    try:
        prefs = await notification_service.get_notification_preferences(user_id)
        return prefs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences: {str(e)}"
        )


@router.put("/preferences", response_model=NotificationPreference)
async def update_notification_preferences(
    enabled_channels: Optional[List[str]] = None,
    enabled_types: Optional[List[str]] = None,
    email_digest: Optional[bool] = None,
    digest_frequency: Optional[str] = None,
    quiet_hours_enabled: Optional[bool] = None,
    quiet_hours_start: Optional[str] = None,
    quiet_hours_end: Optional[str] = None,
    mute_notifications: Optional[bool] = None,
    user_id: str = Depends(verify_token),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Update notification preferences"""
    try:
        channels = [NotificationChannel[c.upper()] for c in enabled_channels] if enabled_channels else None
        types = [NotificationType[t.upper()] for t in enabled_types] if enabled_types else None
        
        prefs = await notification_service.update_notification_preferences(
            user_id=user_id,
            enabled_channels=channels,
            enabled_types=types,
            email_digest=email_digest,
            digest_frequency=digest_frequency,
            quiet_hours_enabled=quiet_hours_enabled,
            quiet_hours_start=quiet_hours_start,
            quiet_hours_end=quiet_hours_end,
            mute_notifications=mute_notifications
        )
        
        return prefs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )
