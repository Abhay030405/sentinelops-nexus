"""
Analytics Routes
Phase 3 API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.analytics.models import (
    AnalyticsReport, TimeRange, AnomalyAlert, LoginAnalytics,
    UserActivityAnalytics, DocumentAnalytics, SecurityAnalytics
)
from app.analytics.services import AnalyticsService
from app.utils.auth import verify_token
from app.utils.rbac import require_role
from app.database.mongodb import get_database
from typing import List

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


async def get_analytics_service(db=Depends(get_database)) -> AnalyticsService:
    """Dependency to get analytics service"""
    return AnalyticsService(db)


@router.get("/report", response_model=AnalyticsReport)
async def get_analytics_report(
    time_range: TimeRange = TimeRange.LAST_7D,
    user_id: str = Depends(verify_token),
    role: str = Depends(require_role(['admin', 'manager'])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get comprehensive analytics report
    Requires admin or manager role
    """
    try:
        report = await analytics_service.generate_full_report(time_range)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/login", response_model=LoginAnalytics)
async def get_login_analytics(
    time_range: TimeRange = TimeRange.LAST_7D,
    user_id: str = Depends(verify_token),
    role: str = Depends(require_role(['admin', 'manager'])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get login statistics"""
    try:
        analytics = await analytics_service.get_login_analytics(time_range)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get login analytics: {str(e)}"
        )


@router.get("/users", response_model=UserActivityAnalytics)
async def get_user_analytics(
    time_range: TimeRange = TimeRange.LAST_7D,
    user_id: str = Depends(verify_token),
    role: str = Depends(require_role(['admin', 'manager'])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get user activity statistics"""
    try:
        analytics = await analytics_service.get_user_activity_analytics(time_range)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user analytics: {str(e)}"
        )


@router.get("/documents", response_model=DocumentAnalytics)
async def get_document_analytics(
    time_range: TimeRange = TimeRange.LAST_7D,
    user_id: str = Depends(verify_token),
    role: str = Depends(require_role(['admin', 'manager'])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get document operation statistics"""
    try:
        analytics = await analytics_service.get_document_analytics(time_range)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document analytics: {str(e)}"
        )


@router.get("/security", response_model=SecurityAnalytics)
async def get_security_analytics(
    time_range: TimeRange = TimeRange.LAST_7D,
    user_id: str = Depends(verify_token),
    role: str = Depends(require_role(['admin'])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get security event statistics"""
    try:
        analytics = await analytics_service.get_security_analytics(time_range)
        return analytics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get security analytics: {str(e)}"
        )


@router.get("/anomalies", response_model=List[AnomalyAlert])
async def detect_anomalies(
    user_id: str = Depends(verify_token),
    role: str = Depends(require_role(['admin'])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Detect and get system anomalies"""
    try:
        alerts = await analytics_service.detect_anomalies()
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect anomalies: {str(e)}"
        )
