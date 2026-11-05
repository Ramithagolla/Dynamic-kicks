from typing import Optional, List, Dict, Any
# pyrefly: ignore[missing-import]
from fastapi import APIRouter, HTTPException, Query, status
from app.services.mongo_service import mongo_service

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

@router.get("")
async def list_incidents(
    severity: Optional[str] = Query(None, description="Filter by severity: Critical, High, Medium, Low"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: open, confirmed, resolved"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """Retrieves list of incidents stored in MongoDB."""
    incidents = await mongo_service.list_incidents(
        severity=severity,
        status=status_filter,
        limit=limit,
        skip=skip
    )
    return {
        "success": True,
        "count": len(incidents),
        "incidents": incidents
    }

@router.get("/{incident_id}")
async def get_incident_details(incident_id: str):
    """Retrieves single incident with its security events and analyst feedback."""
    incident = await mongo_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' was not found in the database."
        )

    # Retrieve associated events and feedback
    events = await mongo_service.get_events_by_incident(incident_id)
    feedback = await mongo_service.get_feedback_by_incident(incident_id)

    return {
        "success": True,
        "incident": incident,
        "events": events,
        "feedback": feedback
    }
