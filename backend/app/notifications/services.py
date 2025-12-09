"""
Notifications Services
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Set
from motor.motor_asyncio import AsyncIOMotorClient
from app.notifications.models import (
    Notification, NotificationType, NotificationPriority, NotificationChannel,
    NotificationPreference, NotificationStats
)


class NotificationService:
    """Notification Management Service"""
    
    def __init__(self, db):
        self.db = db
        self.notifications_collection = db['notifications']
        self.preferences_collection = db['notification_preferences']
        self.delivery_logs_collection = db['notification_delivery_logs']
        self.subscribers: Dict[str, Set[str]] = {}  # user_id -> set of connection_ids
    
    async def send_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        channels: Optional[List[NotificationChannel]] = None,
        data: Optional[Dict] = None,
        action_url: Optional[str] = None,
        expires_in_days: int = 30
    ) -> Notification:
        """Send notification to user"""
        
        # Get user preferences
        prefs = await self.get_notification_preferences(user_id)
        
        # Determine delivery channels
        if channels is None:
            channels = prefs.enabled_channels if prefs else [NotificationChannel.IN_APP]
        
        # Check if notification type is enabled
        if prefs and notification_type not in prefs.enabled_types:
            channels = [NotificationChannel.IN_APP]  # Still send in-app
        
        # Check quiet hours
        if prefs and prefs.quiet_hours_enabled:
            if self._is_in_quiet_hours(prefs):
                # Move non-critical to in-app only
                if priority != NotificationPriority.CRITICAL:
                    channels = [NotificationChannel.IN_APP]
        
        notification_id = str(uuid.uuid4())
        
        notification_doc = {
            'notification_id': notification_id,
            'user_id': user_id,
            'notification_type': notification_type.value,
            'title': title,
            'message': message,
            'priority': priority.value,
            'channels': [c.value for c in channels],
            'data': data or {},
            'created_at': datetime.utcnow(),
            'read_at': None,
            'delivered_at': None,
            'expires_at': datetime.utcnow() + timedelta(days=expires_in_days),
            'is_read': False,
            'action_url': action_url
        }
        
        result = await self.notifications_collection.insert_one(notification_doc)
        
        # Schedule delivery on supported channels
        for channel in channels:
            await self._schedule_delivery(notification_id, user_id, channel, data or {})
        
        return Notification(**notification_doc)
    
    async def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """Mark notification as read"""
        result = await self.notifications_collection.update_one(
            {'notification_id': notification_id, 'user_id': user_id},
            {'$set': {'is_read': True, 'read_at': datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for user"""
        result = await self.notifications_collection.update_many(
            {'user_id': user_id, 'is_read': False},
            {'$set': {'is_read': True, 'read_at': datetime.utcnow()}}
        )
        
        return result.modified_count
    
    async def get_notifications(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        notification_type: Optional[NotificationType] = None,
        is_read: Optional[bool] = None,
        sort_by: str = "-created_at"
    ) -> tuple[List[Notification], int]:
        """Get user's notifications"""
        
        query = {'user_id': user_id}
        
        if notification_type:
            query['notification_type'] = notification_type.value
        
        if is_read is not None:
            query['is_read'] = is_read
        
        # Remove expired notifications
        await self.notifications_collection.delete_many({
            'expires_at': {'$lt': datetime.utcnow()}
        })
        
        # Parse sort_by
        sort_field = sort_by.lstrip('-')
        sort_order = -1 if sort_by.startswith('-') else 1
        
        total = await self.notifications_collection.count_documents(query)
        
        notifications_docs = await self.notifications_collection.find(query).sort(
            sort_field, sort_order
        ).skip(offset).limit(limit).to_list(None)
        
        notifications = [Notification(**doc) for doc in notifications_docs]
        
        return notifications, total
    
    async def delete_notification(self, user_id: str, notification_id: str) -> bool:
        """Delete notification"""
        result = await self.notifications_collection.delete_one({
            'notification_id': notification_id,
            'user_id': user_id
        })
        
        return result.deleted_count > 0
    
    async def get_notification_stats(self, user_id: str) -> NotificationStats:
        """Get notification statistics"""
        
        total = await self.notifications_collection.count_documents({'user_id': user_id})
        unread = await self.notifications_collection.count_documents({
            'user_id': user_id, 'is_read': False
        })
        read = total - unread
        
        # By priority
        by_priority = {}
        for priority in NotificationPriority:
            count = await self.notifications_collection.count_documents({
                'user_id': user_id,
                'priority': priority.value
            })
            by_priority[priority.value] = count
        
        # By type
        by_type = {}
        for notif_type in NotificationType:
            count = await self.notifications_collection.count_documents({
                'user_id': user_id,
                'notification_type': notif_type.value
            })
            by_type[notif_type.value] = count
        
        # Last notification
        last = await self.notifications_collection.find_one(
            {'user_id': user_id},
            sort=[('created_at', -1)]
        )
        
        return NotificationStats(
            user_id=user_id,
            total_notifications=total,
            unread_count=unread,
            read_count=read,
            by_priority=by_priority,
            by_type=by_type,
            last_notification_at=last['created_at'] if last else None
        )
    
    async def update_notification_preferences(
        self,
        user_id: str,
        enabled_channels: Optional[List[NotificationChannel]] = None,
        enabled_types: Optional[List[NotificationType]] = None,
        email_digest: Optional[bool] = None,
        digest_frequency: Optional[str] = None,
        quiet_hours_enabled: Optional[bool] = None,
        quiet_hours_start: Optional[str] = None,
        quiet_hours_end: Optional[str] = None,
        mute_notifications: Optional[bool] = None
    ) -> NotificationPreference:
        """Update user notification preferences"""
        
        update_doc = {'updated_at': datetime.utcnow()}
        
        if enabled_channels is not None:
            update_doc['enabled_channels'] = [c.value for c in enabled_channels]
        
        if enabled_types is not None:
            update_doc['enabled_types'] = [t.value for t in enabled_types]
        
        if email_digest is not None:
            update_doc['email_digest'] = email_digest
        
        if digest_frequency is not None:
            update_doc['digest_frequency'] = digest_frequency
        
        if quiet_hours_enabled is not None:
            update_doc['quiet_hours_enabled'] = quiet_hours_enabled
        
        if quiet_hours_start is not None:
            update_doc['quiet_hours_start'] = quiet_hours_start
        
        if quiet_hours_end is not None:
            update_doc['quiet_hours_end'] = quiet_hours_end
        
        if mute_notifications is not None:
            update_doc['mute_notifications'] = mute_notifications
        
        await self.preferences_collection.update_one(
            {'user_id': user_id},
            {'$set': update_doc},
            upsert=True
        )
        
        prefs = await self.get_notification_preferences(user_id)
        return prefs
    
    async def get_notification_preferences(self, user_id: str) -> Optional[NotificationPreference]:
        """Get user notification preferences"""
        prefs_doc = await self.preferences_collection.find_one({'user_id': user_id})
        
        if not prefs_doc:
            # Return defaults
            return NotificationPreference(user_id=user_id)
        
        return NotificationPreference(**prefs_doc)
    
    def register_connection(self, user_id: str, connection_id: str) -> None:
        """Register WebSocket connection"""
        if user_id not in self.subscribers:
            self.subscribers[user_id] = set()
        
        self.subscribers[user_id].add(connection_id)
    
    def unregister_connection(self, user_id: str, connection_id: str) -> None:
        """Unregister WebSocket connection"""
        if user_id in self.subscribers:
            self.subscribers[user_id].discard(connection_id)
            
            if not self.subscribers[user_id]:
                del self.subscribers[user_id]
    
    def get_user_connections(self, user_id: str) -> Set[str]:
        """Get all active connections for user"""
        return self.subscribers.get(user_id, set()).copy()
    
    async def _schedule_delivery(
        self,
        notification_id: str,
        user_id: str,
        channel: NotificationChannel,
        data: Dict
    ) -> None:
        """Schedule notification delivery on specific channel"""
        log_doc = {
            'notification_id': notification_id,
            'user_id': user_id,
            'channel': channel.value,
            'scheduled_at': datetime.utcnow(),
            'delivered_at': None,
            'status': 'scheduled'
        }
        
        await self.delivery_logs_collection.insert_one(log_doc)
        
        # In production, integrate with actual delivery services
        # Email: AWS SES, SendGrid, etc.
        # SMS: Twilio, AWS SNS, etc.
        # Push: Firebase, OneSignal, etc.
    
    def _is_in_quiet_hours(self, prefs: NotificationPreference) -> bool:
        """Check if current time is within quiet hours"""
        if not prefs.quiet_hours_enabled:
            return False
        
        current_time = datetime.utcnow().time()
        start_time = datetime.strptime(prefs.quiet_hours_start, '%H:%M').time() if prefs.quiet_hours_start else None
        end_time = datetime.strptime(prefs.quiet_hours_end, '%H:%M').time() if prefs.quiet_hours_end else None
        
        if not start_time or not end_time:
            return False
        
        # Handle overnight quiet hours
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            return current_time >= start_time or current_time <= end_time
