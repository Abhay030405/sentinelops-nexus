"""
Data Export Models and Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ExportFormat(str, Enum):
    """Supported export formats"""
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"
    PDF = "pdf"


class ExportDataType(str, Enum):
    """Types of data to export"""
    USERS = "users"
    DOCUMENTS = "documents"
    AUDIT_LOGS = "audit_logs"
    LOGIN_LOGS = "login_logs"
    ACTIVITY_LOGS = "activity_logs"
    ALL = "all"


class ExportRequest(BaseModel):
    """Data export request"""
    data_type: ExportDataType
    export_format: ExportFormat
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    filters: Dict[str, Any] = Field(default={})
    include_metadata: bool = Field(default=True)


class ExportJob(BaseModel):
    """Export job tracking"""
    export_id: str
    user_id: str
    data_type: ExportDataType
    export_format: ExportFormat
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime]
    file_path: Optional[str]
    file_size: Optional[int]
    record_count: int
    error_message: Optional[str]
    expires_at: Optional[datetime]


class ExportJobResponse(BaseModel):
    """Response for export job"""
    export_id: str
    status: str
    message: str
    download_url: Optional[str]


class AuditLog(BaseModel):
    """Audit log entry"""
    audit_id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str  # success, failed
    changes: Optional[Dict[str, Any]]  # Before/after changes


class AuditLogFilter(BaseModel):
    """Filter for audit logs"""
    user_id: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class AuditStats(BaseModel):
    """Audit statistics"""
    total_events: int
    events_by_action: Dict[str, int]
    events_by_resource: Dict[str, int]
    success_rate: float
    most_active_users: List[Dict[str, Any]]
    period_start: datetime
    period_end: datetime


class DataRetention(BaseModel):
    """Data retention policy"""
    retention_days: int = Field(default=90, ge=1)
    auto_delete_enabled: bool = Field(default=True)
    archive_before_delete: bool = Field(default=True)
    archive_format: Optional[ExportFormat] = None
    encryption_enabled: bool = Field(default=True)
