"""
Notifications Models and Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Types of notifications"""
    SECURITY_ALERT = "security_alert"
    USER_ACTIVITY = "user_activity"
    SYSTEM_UPDATE = "system_update"
    DOCUMENT_READY = "document_ready"
    LOGIN_ATTEMPT = "login_attempt"
    ROLE_CHANGE = "role_change"
    CUSTOM = "custom"


class NotificationPriority(str, Enum):
    """Notification priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NotificationChannel(str, Enum):
    """Notification delivery channels"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"


class Notification(BaseModel):
    """Notification model"""
    notification_id: str
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.MEDIUM
    channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    data: Dict[str, Any] = Field(default={}, description="Additional data payload")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_read: bool = False
    action_url: Optional[str] = None


class NotificationPreference(BaseModel):
    """User notification preferences"""
    user_id: str
    enabled_channels: List[NotificationChannel] = [NotificationChannel.IN_APP]
    enabled_types: List[NotificationType] = Field(default=[NotificationType.SECURITY_ALERT])
    email_digest: bool = True
    digest_frequency: str = Field(default="daily")  # daily, weekly, never
    quiet_hours_enabled: bool = False
    quiet_hours_start: Optional[str] = None  # HH:MM
    quiet_hours_end: Optional[str] = None
    mute_notifications: bool = False
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    message_type: str  # notification, update, error
    event: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NotificationStats(BaseModel):
    """Notification statistics"""
    user_id: str
    total_notifications: int
    unread_count: int
    read_count: int
    by_priority: Dict[str, int]
    by_type: Dict[str, int]
    last_notification_at: Optional[datetime]


class NotificationQuery(BaseModel):
    """Query parameters for notifications"""
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    is_read: Optional[bool] = None
    sort_by: str = Field(default="-created_at")  # Supports: created_at, priority, etc.
