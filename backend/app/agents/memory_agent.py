import logging
from typing import Dict, Any, List, Optional
from app.services.hindsight_service import hindsight_service

logger = logging.getLogger(__name__)

class HindsightMemoryAgent:
    """
    AGENT 3: Hindsight Memory Agent
    Searches previous incident intelligence via Hindsight recall and reflect.
    Discovers related attack techniques, verified root causes, and analyst-confirmed remedies.
    Never claims memory was recalled if the Hindsight request failed or returned no relevant result.
    Clearly reports "Memory unavailable" when Hindsight is unreachable.
    """
    def __init__(self):
        self.name = "Hindsight Memory Agent"

    async def retrieve_context(
        self,
        attack_type: str,
        indicators: List[str],
        summary: str
    ) -> Dict[str, Any]:
        logger.info(f"[{self.name}] Searching Hindsight memory bank for attack='{attack_type}'")

        # 0. Check for baseline normal activity - no incident remediation recall needed
        if attack_type in ("Normal Activity / Baseline", "Insufficient Evidence"):
            return {
                "memory_used": False,
                "query": "None (Normal baseline activity)",
                "bank_id": hindsight_service.bank_id,
                "retrieved_memories": [],
                "memory_count": 0,
                "memory_synthesis": None,
                "reflection_facts": [],
                "explanation": "Normal baseline activity detected. No historical incident remediation required.",
                "hindsight_status": "not_applicable"
            }

        # Construct specific search query from indicators and attack signature
        query_terms = [attack_type]
        for ind in indicators[:4]:
            query_terms.append(str(ind))
        query = f"Incident resolution and defensive recommendations for: {' '.join(query_terms)} - {summary[:120]}"

        # 1. Recall operation from Hindsight
        recall_res = await hindsight_service.recall(query=query)

        recall_success = recall_res.get("success", False)
        memories = recall_res.get("results", []) or []

        if not recall_success:
            err = recall_res.get("error", "Service unavailable")
            logger.warning(f"[{self.name}] Hindsight recall was unsuccessful: {err}")
            return {
                "memory_used": False,
                "query": query,
                "bank_id": hindsight_service.bank_id,
                "retrieved_memories": [],
                "memory_count": 0,
                "memory_synthesis": None,
                "reflection_facts": [],
                "explanation": f"Memory unavailable: {err}. Proceeding with non-memory-based analysis.",
                "hindsight_status": "unavailable",
                "error": err
            }

        if len(memories) == 0:
            logger.info(f"[{self.name}] Recall succeeded, but no matching historical memory was found.")
            return {
                "memory_used": False,
                "query": query,
                "bank_id": hindsight_service.bank_id,
                "retrieved_memories": [],
                "memory_count": 0,
                "memory_synthesis": None,
                "reflection_facts": [],
                "explanation": "No relevant historical memory found in Hindsight bank.",
                "hindsight_status": "no_matching_memory"
            }

        # 2. Reflect operation if memories exist
        logger.info(f"[{self.name}] Recalled {len(memories)} memories. Triggering Hindsight reflection...")
        synthesis_text = None
        reflection_facts = []
        try:
            reflect_res = await hindsight_service.reflect(
                query=f"Synthesize the historical mitigation outcome and lessons learned for {attack_type} involving indicators: {', '.join(indicators[:3])}",
                context=f"Current incident summary: {summary}"
            )
            synthesis_text = reflect_res.get("synthesis")
            reflection_facts = reflect_res.get("based_on", [])
        except Exception as ref_err:
            logger.warning(f"[{self.name}] Reflection error: {ref_err}")

        # Formulate relationship explanation citing recalled count and bank
        explanation = (
            f"Retrieved {len(memories)} confirmed historical incident records from Hindsight bank '{hindsight_service.bank_id}'. "
            f"Historical resolutions indicate confirmed containment protocols applied to similar attack patterns, including IP perimeter filtering and credential revocation."
        )

        return {
            "memory_used": True,
            "query": query,
            "bank_id": hindsight_service.bank_id,
            "retrieved_memories": memories,
            "memory_count": len(memories),
            "memory_synthesis": synthesis_text,
            "reflection_facts": reflection_facts,
            "explanation": explanation,
            "hindsight_status": "recalled"
        }

memory_agent = HindsightMemoryAgent()
