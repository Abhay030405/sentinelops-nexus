"""
Facility Ops Hub Routes
API endpoints for Issue Tracking System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database.mongodb import get_database
from app.utils.dependencies import get_current_user
from app.facility_ops.models import (
    IssueCreate, IssueResponse, IssueUpdate, IssueAssign,
    IssueOutcomeSubmit, IssueStatusUpdate, IssueStatus
)
from app.facility_ops.services import FacilityOpsService

router = APIRouter(prefix="/facility-ops", tags=["Facility Operations"])


def get_facility_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> FacilityOpsService:
    """Dependency to get facility ops service"""
    return FacilityOpsService(db)


@router.post("/issues", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
async def create_issue(
    issue_data: IssueCreate,
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Create a new issue (Admin or Agent only)
    
    **Permissions:**
    - Admin: Can create issues
    - Agent: Can create issues
    - Technician: Cannot create issues
    """
    user_role = current_user.get("role")
    user_id = str(current_user.get("_id"))
    
    # Permission check: Only admin and agent can create issues
    if user_role not in ["admin", "agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and agents can create issues"
        )
    
    try:
        issue = await service.create_issue(issue_data, user_id, user_role)
        return issue
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/issues", response_model=List[IssueResponse])
async def get_all_issues(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    include_completed: bool = Query(False, description="Include completed issues"),
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Get all active issues (excludes completed issues by default)
    
    **Permissions:**
    - Admin: Can see all issues
    - Agent: Can see all issues
    - Technician: Can only see issues assigned to them
    
    **Query Parameters:**
    - status_filter: Optional filter by status (pending, in_progress)
    - include_completed: Set to true to include completed issues (default: false)
    
    **Note:** Completed/solved issues are moved to a separate endpoint /issues/solved
    """
    user_role = current_user.get("role")
    user_id = str(current_user.get("_id"))
    
    try:
        issues = await service.get_all_issues(user_role, user_id, status_filter, include_completed)
        return issues
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/issues/solved", response_model=List[IssueResponse])
async def get_solved_issues(
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Get all solved/completed issues separately
    
    **Permissions:**
    - Admin: Can see all completed issues
    - Agent: Can see all completed issues
    - Technician: Can only see completed issues they worked on
    
    **Returns:**
    - List of completed issues sorted by completion date (most recent first)
    """
    user_role = current_user.get("role")
    user_id = str(current_user.get("_id"))
    
    try:
        issues = await service.get_solved_issues(user_role, user_id)
        return issues
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/issues/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: str,
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Get single issue by ID
    
    **Permissions:**
    - Admin: Can see any issue
    - Agent: Can see any issue
    - Technician: Can only see issues assigned to them
    """
    user_role = current_user.get("role")
    user_id = str(current_user.get("_id"))
    
    try:
        issue = await service.get_issue_by_id(issue_id, user_role, user_id)
        if not issue:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        return issue
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/issues/{issue_id}/assign", response_model=IssueResponse)
async def assign_issue_to_technician(
    issue_id: str,
    assign_data: IssueAssign,
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Assign issue to a technician (Admin only)
    
    **Permissions:**
    - Admin only
    
    **Business Logic:**
    - Issue status changes from PENDING to IN_PROGRESS
    - Technician must be active
    - Activity log is updated
    """
    user_role = current_user.get("role")
    
    # Permission check: Only admin can assign
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can assign issues"
        )
    
    admin_id = str(current_user.get("_id"))
    admin_name = current_user.get("full_name", "Admin")
    
    try:
        issue = await service.assign_issue(issue_id, assign_data, admin_id, admin_name)
        return issue
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/issues/{issue_id}/outcome", response_model=IssueResponse)
async def submit_work_outcome(
    issue_id: str,
    outcome_data: IssueOutcomeSubmit,
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Submit work outcome (Technician only)
    
    **Permissions:**
    - Technician only (must be assigned to this issue)
    
    **Business Logic:**
    - If SUCCESS: Issue status → COMPLETED, Technician score +50
    - If FAILED: Issue status → PENDING (for reassignment), Technician score -25
    - Activity log is updated
    """
    user_role = current_user.get("role")
    
    # Permission check: Only technician can submit outcome
    if user_role != "technician":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only technicians can submit work outcomes"
        )
    
    technician_id = str(current_user.get("_id"))
    technician_name = current_user.get("full_name", "Technician")
    
    try:
        issue = await service.submit_outcome(issue_id, outcome_data, technician_id, technician_name)
        return issue
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/issues/{issue_id}/status", response_model=IssueResponse)
async def update_issue_status(
    issue_id: str,
    status_data: IssueStatusUpdate,
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Update issue status (Admin only)
    
    **Permissions:**
    - Admin only
    
    **Use Cases:**
    - Admin can mark issue as COMPLETED after technician success
    - Admin can move issue back to PENDING if needed
    - Admin can change status based on review
    """
    user_role = current_user.get("role")
    
    # Permission check: Only admin can update status
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update issue status"
        )
    
    admin_id = str(current_user.get("_id"))
    admin_name = current_user.get("full_name", "Admin")
    
    try:
        issue = await service.update_issue_status(issue_id, status_data, admin_id, admin_name)
        return issue
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/issues/{issue_id}", status_code=status.HTTP_200_OK)
async def delete_issue(
    issue_id: str,
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Delete an issue (Admin only)
    
    **Permissions:**
    - Admin only
    """
    user_role = current_user.get("role")
    
    # Permission check: Only admin can delete
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete issues"
        )
    
    admin_id = str(current_user.get("_id"))
    
    print(f"Attempting to delete issue: {issue_id}")
    print(f"Admin ID: {admin_id}")
    
    try:
        deleted = await service.delete_issue(issue_id, admin_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
        return {"message": "Issue deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete issue error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete issue: {str(e)}")


@router.get("/technicians", response_model=List[dict])
async def get_available_technicians(
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Get list of available technicians with their scores (Admin only)
    
    **Permissions:**
    - Admin only
    
    **Returns:**
    - List of active technicians sorted by score (highest first)
    - Each technician has: id, name, score, status
    - Default score: 100
    """
    user_role = current_user.get("role")
    
    # Permission check: Only admin can view technicians
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view technicians list"
        )
    
    try:
        technicians = await service.get_available_technicians()
        return technicians
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats", response_model=dict)
async def get_issue_statistics(
    current_user: dict = Depends(get_current_user),
    service: FacilityOpsService = Depends(get_facility_service)
):
    """
    Get issue statistics for dashboard
    
    **Permissions:**
    - Admin and Agent only
    
    **Returns:**
    - total: Total number of issues
    - pending: Issues waiting for assignment
    - in_progress: Issues being worked on
    - completed: Completed issues
    - high_priority_open: High priority issues not completed
    """
    user_role = current_user.get("role")
    
    # Permission check: Admin and Agent only
    if user_role not in ["admin", "agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and agents can view statistics"
        )
    
    try:
        stats = await service.get_issue_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
