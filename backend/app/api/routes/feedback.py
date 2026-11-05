import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import FeedbackCreate
from app.services.mongo_service import mongo_service
from app.agents.learning_agent import learning_agent

router = APIRouter(prefix="/api/incidents", tags=["Feedback"])

@router.post("/{incident_id}/feedback")
async def submit_analyst_feedback(incident_id: str, feedback: FeedbackCreate):
    """
    Submits analyst review and confirmed resolution for an incident.
    Invokes Agent 5 (Learning Agent) to retain verified knowledge into Hindsight.
    Stores feedback in MongoDB.
    """
    incident = await mongo_service.get_incident(incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )

    feedback_dict = feedback.model_dump()
    feedback_dict["feedback_id"] = f"FB-{uuid.uuid4().hex[:8].upper()}"
    feedback_dict["incident_id"] = incident_id
    feedback_dict["created_at"] = datetime.now(timezone.utc).isoformat()

    # Trigger Agent 5 (Learning Agent) to retain into Hindsight
    learning_result = await learning_agent.learn(incident, feedback_dict)

    feedback_dict["retention_status"] = learning_result.get("retention_status", "pending")
    feedback_dict["retention_details"] = learning_result

    # Persist in MongoDB
    await mongo_service.save_feedback(feedback_dict)

    return {
        "success": True,
        "message": "Analyst feedback submitted and processed by Learning Agent.",
        "retention_status": feedback_dict["retention_status"],
        "hindsight_retention": learning_result,
        "feedback": feedback_dict
    }
