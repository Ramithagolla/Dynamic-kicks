from typing import Dict, Any, List
from fastapi import APIRouter
from app.services.mongo_service import mongo_service
from app.services.hindsight_service import hindsight_service
from app.services.llm_service import llm_service
from app.config import settings

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("")
@router.get("/summary")
async def get_analytics_metrics() -> Dict[str, Any]:
    """
    Returns consolidated SOC analytics, metrics, recommendation acceptance rates,
    threat severity distribution, defensive action activity, agent mesh statuses,
    and memory-assisted investigation comparison data.
    """
    summary = await mongo_service.get_analytics()
    incidents = await mongo_service.list_incidents(limit=25)

    # Separate into non-memory vs memory-assisted for comparison
    non_memory_incidents = [i for i in incidents if not i.get("memory_used")]
    memory_assisted_incidents = [i for i in incidents if i.get("memory_used")]

    # Real threat severity distribution from database records
    severity_distribution = [
        {"name": "Critical", "value": summary["critical_count"], "color": "#EF4444"},
        {"name": "High", "value": summary["high_count"], "color": "#F97316"},
        {"name": "Medium", "value": summary["medium_count"], "color": "#EAB308"},
        {"name": "Low", "value": summary["low_count"], "color": "#10B981"}
    ]

    # Real incident activity timeline (ordered chronologically from oldest to newest)
    activity_timeline = []
    for inc in reversed(incidents[:12]):
        created_val = inc.get("created_at", "")
        time_display = created_val[11:16] if len(created_val) >= 16 else "Now"
        date_display = created_val[:10] if len(created_val) >= 10 else "Today"
        inc_id = inc.get("incident_id", "TL-UNKNOWN")
        short_id = inc_id.split("-")[-1] if "-" in inc_id else inc_id[:6]

        activity_timeline.append({
            "id": inc_id,
            "name": short_id,
            "full_id": inc_id,
            "title": inc.get("title", "Security Incident"),
            "date": date_display,
            "time": time_display,
            "timestamp": created_val,
            "severity": inc.get("severity", "Medium"),
            "memory_used": inc.get("memory_used", False),
            "hindsight_status": inc.get("hindsight_status", "no_matching_memory"),
            "recommendations_count": len(inc.get("recommendations", [])),
            "analyzed_events_count": inc.get("analyzed_events_count", inc.get("event_count", 0)),
            "status": inc.get("status", "open")
        })

    # Check live services for agent status verification
    hindsight_health = await hindsight_service.check_health()
    mongo_health = await mongo_service.check_health()
    groq_health = await llm_service.check_health()

    agent_mesh = [
        {
            "id": "detection",
            "name": "Threat Detection Agent",
            "role": "Rule execution & log pattern analysis",
            "status": "available",
            "engine": "Hybrid (Rules + Groq)" if groq_health.get("status") == "connected" else "Deterministic Rule Engine",
            "execution_count": summary["agent_execution_stats"]["detection"]["total"]
        },
        {
            "id": "investigation",
            "name": "Investigation Agent",
            "role": "Timeline synthesis & hypothesis correlation",
            "status": "available",
            "engine": "Groq LLM" if groq_health.get("status") == "connected" else "Deterministic Graph Synthesizer",
            "execution_count": summary["agent_execution_stats"]["investigation"]["total"]
        },
        {
            "id": "memory",
            "name": "Hindsight Memory Agent",
            "role": "Recall & reflect across memory bank",
            "status": "available" if hindsight_health.get("status") == "connected" else "unavailable",
            "engine": f"Hindsight Cloud ({settings.HINDSIGHT_BANK_ID})" if hindsight_health.get("status") == "connected" else "Memory Service Offline",
            "execution_count": summary["agent_execution_stats"]["memory"]["total"]
        },
        {
            "id": "response",
            "name": "Response Recommendation Agent",
            "role": "Defensive recommendations formulation",
            "status": "available",
            "engine": "Advisory Playbook + Groq",
            "execution_count": summary["agent_execution_stats"]["response"]["total"]
        },
        {
            "id": "learning",
            "name": "Learning Agent",
            "role": "Durable knowledge retention post-review",
            "status": "available" if (hindsight_health.get("status") == "connected" and mongo_health.get("status") == "connected") else "degraded",
            "engine": "Analyst-Verified Hindsight Retain",
            "execution_count": summary["agent_execution_stats"]["learning"]["total"]
        }
    ]

    # Before and after comparison demonstration payload
    comparison = {
        "has_comparison": len(non_memory_incidents) > 0 and len(memory_assisted_incidents) > 0,
        "first_investigation": non_memory_incidents[-1] if non_memory_incidents else None,
        "second_investigation": memory_assisted_incidents[0] if memory_assisted_incidents else None,
        "insights": {
            "first_investigation_memory_count": 0,
            "second_investigation_memory_count": len(memory_assisted_incidents[0].get("retrieved_memories", [])) if memory_assisted_incidents else 0,
            "memory_influence": memory_assisted_incidents[0].get("memory_explanation") if memory_assisted_incidents else "Run a second investigation on a similar incident after retaining memory to see direct comparison."
        }
    }

    return {
        "metrics": summary,
        "severity_distribution": severity_distribution,
        "activity_timeline": activity_timeline,
        "agent_mesh": agent_mesh,
        "comparison": comparison,
        "recent_incidents": incidents[:6],
        "hindsight_info": {
            "status": hindsight_health.get("status"),
            "bank_id": settings.HINDSIGHT_BANK_ID,
            "memory_recalled_operations": summary["memory_recalled_count"],
            "memory_retained_operations": summary["memory_retained_count"]
        },
        "database_info": {
            "status": mongo_health.get("status"),
            "mode": mongo_health.get("mode"),
            "database": mongo_health.get("database")
        }
    }
