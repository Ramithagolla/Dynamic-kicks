import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import InvestigateRequest
from app.agents.coordinator import coordinator

router = APIRouter(prefix="/api/investigate", tags=["Investigations"])

@router.post("")
async def start_investigation(request: InvestigateRequest):
    """
    Executes the 5-agent investigation pipeline on security log events.
    1. Threat Detection Agent analyzes logs & calculates deterministic risk.
    2. Investigation Agent synthesizes timeline, facts vs hypotheses.
    3. Hindsight Memory Agent recalls previous incident resolutions & reflects.
    4. Response Recommendation Agent produces prioritized defensive actions.
    5. Incident saved to MongoDB.
    """
    events = request.events or []

    # If dataset_name was specified, load from synthetic sample data
    if not events and request.dataset_name:
        sample_dir = Path(__file__).resolve().parent.parent.parent / "sample_data"
        file_path = sample_dir / f"{request.dataset_name}.json"
        if not file_path.exists():
            file_path = sample_dir / f"{request.dataset_name}.csv"

        if file_path.exists():
            from app.services.log_parser import parse_security_logs
            with open(file_path, "rb") as f:
                events, rejected_cnt, parse_errs, _ = parse_security_logs(file_path.name, f.read())

    if not events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No events provided. Upload a security log file or select a sample dataset."
        )

    # Validate that events contain at least one meaningful record
    valid_records = [
        e for e in events
        if any(e.get(k) and str(e.get(k)).strip() not in ("unknown", "n/a", "127.0.0.1", "")
               for k in ("source_ip", "username", "event_type", "status", "raw_message"))
    ]
    if not valid_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided events contain only empty or placeholder values. Insufficient evidence to execute investigation."
        )

    try:
        pipeline_output = await coordinator.execute_investigation_pipeline(
            events=events,
            title_override=request.title
        )
        return {
            "success": True,
            "incident_id": pipeline_output["incident"]["incident_id"],
            "data": pipeline_output
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation pipeline encountered an error: {str(e)}"
        )
