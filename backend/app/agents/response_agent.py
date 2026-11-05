import logging
from typing import Dict, Any, List
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class ResponseRecommendationAgent:
    """
    AGENT 4: Response Recommendation Agent
    Proposes prioritized defensive remediation actions informed by current investigation
    findings and historical resolution memories from Hindsight.
    All actions strictly mandate human approval.
    """
    def __init__(self):
        self.name = "Response Recommendation Agent"

    async def recommend(
        self,
        investigation_report: Dict[str, Any],
        memory_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(f"[{self.name}] Formulating response recommendations")

        retrieved_memories = memory_context.get("retrieved_memories", [])
        memory_synthesis = memory_context.get("memory_synthesis")

        recommendations_payload = await llm_service.generate_response_recommendations(
            investigation_report=investigation_report,
            historical_memories=retrieved_memories,
            memory_synthesis=memory_synthesis
        )

        actions = recommendations_payload.get("recommended_actions", [])

        # Strict safety guard: enforce requires_human_approval = True and executed = False
        for act in actions:
            act["requires_human_approval"] = True
            act["executed"] = False

        logger.info(f"[{self.name}] Formulated {len(actions)} prioritized recommendations (Requires human approval: True)")
        return {
            "recommended_actions": actions,
            "response_summary": recommendations_payload.get("response_summary", ""),
            "memory_impact_statement": recommendations_payload.get(
                "memory_impact_statement",
                memory_context.get("explanation", "Recommendations generated from current telemetry.")
            )
        }

response_agent = ResponseRecommendationAgent()
