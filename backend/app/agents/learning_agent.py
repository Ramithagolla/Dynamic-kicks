import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.services.hindsight_service import hindsight_service

logger = logging.getLogger(__name__)

class LearningAgent:
    """
    AGENT 5: Learning Agent
    Learns verified incident outcomes confirmed by human security analysts.
    Stores durable knowledge into Hindsight via retain.
    Explicitly refuses to learn unverified AI assumptions.
    """
    def __init__(self):
        self.name = "Learning Agent"

    async def learn(
        self,
        incident: Dict[str, Any],
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        incident_id = incident.get("incident_id")
        finding_confirmed = feedback.get("finding_confirmed", False)
        confirmed_root_cause = feedback.get("confirmed_root_cause", "")
        resolution_notes = feedback.get("resolution_notes", "")
        accepted_recs = feedback.get("accepted_recommendations", [])
        rejected_recs = feedback.get("rejected_recommendations", [])
        attack_type = incident.get("attack_type", "Security Incident")
        indicators = incident.get("indicators", [])

        logger.info(f"[{self.name}] Processing analyst confirmation for incident {incident_id}")

        if not finding_confirmed:
            logger.info(f"[{self.name}] Analyst marked finding as unconfirmed/false-positive. Retaining dismissal note to avoid false positives.")
            content = (
                f"ThreatLens Confirmed False-Positive / Dismissed Incident: {incident_id}\n"
                f"Attack Type Flagged: {attack_type}\n"
                f"Analyst Determination: Incident was rejected or flagged as benign activity.\n"
                f"Resolution Notes: {resolution_notes}\n"
                f"Indicators: {', '.join(str(i) for i in indicators)}"
            )
            tags = ["threatlens", "false-positive", "benign"]
        else:
            # Verified incident knowledge
            content = (
                f"ThreatLens Confirmed Security Incident Resolution: {incident_id}\n"
                f"Attack Classification: {attack_type}\n"
                f"Analyst Confirmed Root Cause: {confirmed_root_cause}\n"
                f"Resolution & Containment Notes: {resolution_notes}\n"
                f"Accepted Defensive Recommendations: {', '.join(accepted_recs) if accepted_recs else 'None'}\n"
                f"Rejected Recommendations: {', '.join(rejected_recs) if rejected_recs else 'None'}\n"
                f"Correlated Indicators: {', '.join(str(i) for i in indicators)}\n"
                f"Severity: {incident.get('severity', 'Medium')}\n"
                f"Confirmation Timestamp: {datetime.now(timezone.utc).isoformat()}"
            )
            tags = ["threatlens", "incident-resolution", attack_type.lower().replace(" ", "-")]

        metadata = {
            "incident_id": str(incident_id),
            "attack_type": str(attack_type),
            "confirmed_by_analyst": str(finding_confirmed),
            "source": "threatlens_analyst_feedback"
        }

        # Retain into Hindsight
        retain_result = await hindsight_service.retain(
            content=content,
            context=f"Analyst resolution for incident {incident_id}",
            document_id=f"incident-{incident_id}",
            metadata=metadata,
            tags=tags
        )

        success = retain_result.get("success", False)
        status_label = "succeeded" if success else "failed"

        logger.info(f"[{self.name}] Hindsight retain status: {status_label}")

        return {
            "retention_status": status_label,
            "success": success,
            "bank_id": hindsight_service.bank_id,
            "document_id": f"incident-{incident_id}",
            "details": retain_result,
            "learned_facts": {
                "incident_id": incident_id,
                "confirmed_root_cause": confirmed_root_cause,
                "accepted_actions": accepted_recs,
                "rejected_actions": rejected_recs
            }
        }

learning_agent = LearningAgent()
