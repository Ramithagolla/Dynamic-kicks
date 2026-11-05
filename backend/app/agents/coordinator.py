import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.agents.detection_agent import detection_agent
from app.agents.investigation_agent import investigation_agent
from app.agents.memory_agent import memory_agent
from app.agents.response_agent import response_agent
from app.services.mongo_service import mongo_service

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """
    Multi-Agent Coordinator orchestrating:
    1. Threat Detection Agent
    2. Investigation Agent
    3. Hindsight Memory Agent
    4. Response Recommendation Agent
    5. Learning Agent (post-analyst feedback)
    Persists unified state in MongoDB collections.
    """
    def __init__(self):
        self.name = "Coordinator Agent"

    async def execute_investigation_pipeline(
        self,
        events: List[Dict[str, Any]],
        title_override: Optional[str] = None
    ) -> Dict[str, Any]:
        incident_id = f"TL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        logger.info(f"[{self.name}] Initiating investigation pipeline for {incident_id} with {len(events)} events")

        # Associate events with this incident ID
        for ev in events:
            ev["incident_id"] = incident_id

        # Compute core event counts and attributes from actual log records
        failed_statuses = ("failed", "failure", "denied", "blocked")
        suspicious_events_count = sum(1 for e in events if str(e.get("status", "")).lower() in failed_statuses)

        extracted_source_ips = sorted(list(set(
            str(e.get("source_ip", "")).strip()
            for e in events
            if str(e.get("source_ip", "")).strip() and str(e.get("source_ip", "")).strip().lower() not in ("unknown", "n/a", "none")
        )))

        extracted_users = sorted(list(set(
            str(e.get("username", "")).strip()
            for e in events
            if str(e.get("username", "")).strip() and str(e.get("username", "")).strip().lower() not in ("unknown", "n/a", "none")
        )))

        # Tracking live agent statuses
        agent_statuses = {
            "detection": {"name": "Threat Detection Agent", "status": "running", "role": "Rule execution & log pattern analysis"},
            "investigation": {"name": "Investigation Agent", "status": "pending", "role": "Timeline creation & hypothesis testing"},
            "memory": {"name": "Hindsight Memory Agent", "status": "pending", "role": "Recall & reflect across memory bank"},
            "response": {"name": "Response Recommendation Agent", "status": "pending", "role": "Defensive recommendations formulation"},
            "learning": {"name": "Learning Agent", "status": "pending_analyst_review", "role": "Durable knowledge retention post-review"}
        }

        # STEP 1: Detection Agent
        detection_result = await detection_agent.detect(events)
        agent_statuses["detection"]["status"] = "completed"
        agent_statuses["detection"]["findings_count"] = len(detection_result.get("findings", []))

        # STEP 2: Investigation Agent
        agent_statuses["investigation"]["status"] = "running"
        investigation_report = await investigation_agent.investigate(events, detection_result)
        agent_statuses["investigation"]["status"] = "completed"
        agent_statuses["investigation"]["timeline_stages"] = len(investigation_report.get("timeline", []))

        # STEP 3: Hindsight Memory Agent
        agent_statuses["memory"]["status"] = "running"
        attack_type = detection_result.get("attack_type", "Suspicious Incident")
        indicators = detection_result.get("indicators", []) or extracted_source_ips
        summary = investigation_report.get("summary", "")

        memory_context = await memory_agent.retrieve_context(
            attack_type=attack_type,
            indicators=indicators,
            summary=summary
        )
        hsk_status = memory_context.get("hindsight_status", "no_matching_memory")
        agent_statuses["memory"]["status"] = "completed" if hsk_status != "unavailable" else "failed"
        agent_statuses["memory"]["memory_count"] = memory_context.get("memory_count", 0)
        agent_statuses["memory"]["hindsight_status"] = hsk_status

        # STEP 4: Response Recommendation Agent
        agent_statuses["response"]["status"] = "running"
        response_result = await response_agent.recommend(
            investigation_report=investigation_report,
            memory_context=memory_context
        )
        agent_statuses["response"]["status"] = "completed"
        agent_statuses["response"]["recommendations_count"] = len(response_result.get("recommended_actions", []))

        # STEP 5: Construct Unified Incident Record
        title = title_override or investigation_report.get("title", f"Investigation: {attack_type}")
        incident_record = {
            "incident_id": incident_id,
            "title": title,
            "severity": detection_result.get("severity", "Medium"),
            "status": "open",
            "attack_type": attack_type,
            "indicators": indicators,
            "source_ips": extracted_source_ips,
            "targeted_users": extracted_users,
            "analyzed_events_count": len(events),
            "suspicious_events_count": suspicious_events_count,
            "findings": detection_result.get("findings", []),
            "recommendations": response_result.get("recommended_actions", []),
            "timeline": investigation_report.get("timeline", []),
            "hypotheses": investigation_report.get("hypotheses", []),
            "observed_facts": investigation_report.get("observed_facts", []),
            "limitations": investigation_report.get("limitations", []),
            "memory_used": memory_context.get("memory_used", False),
            "hindsight_status": hsk_status,
            "retrieved_memories": memory_context.get("retrieved_memories", []),
            "memory_synthesis": memory_context.get("memory_synthesis"),
            "memory_explanation": memory_context.get("explanation"),
            "response_summary": response_result.get("response_summary"),
            "agent_execution": agent_statuses,
            "event_count": len(events),
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Persist to MongoDB collections
        await mongo_service.save_events(events)
        await mongo_service.save_incident(incident_record)

        logger.info(f"[{self.name}] Pipeline completed successfully for incident {incident_id}. Memory used: {incident_record['memory_used']}")

        return {
            "incident": incident_record,
            "detection": detection_result,
            "investigation": investigation_report,
            "memory": memory_context,
            "response": response_result,
            "agent_execution": agent_statuses
        }

coordinator = AgentCoordinator()
