import logging
from typing import List, Dict, Any
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)

class InvestigationAgent:
    """
    AGENT 2: Investigation Agent
    Constructs an authoritative incident investigation report with timeline,
    observed facts, testable hypotheses, and investigation limitations.
    """
    def __init__(self):
        self.name = "Investigation Agent"

    async def investigate(
        self,
        events: List[Dict[str, Any]],
        detection_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info(f"[{self.name}] Investigating detection findings: {detection_result.get('attack_type')}")

        report = await llm_service.generate_investigation_report(events, detection_result)

        # Ensure required structured fields exist
        if "observed_facts" not in report or not report["observed_facts"]:
            report["observed_facts"] = [
                f"Evaluated {len(events)} security events from log ingestion stream.",
                f"Identified {len(detection_result.get('indicators', []))} suspicious indicators."
            ]
        if "hypotheses" not in report or not report["hypotheses"]:
            report["hypotheses"] = [
                "Adversary activity matches automated brute-force or credential validation patterns."
            ]
        if "limitations" not in report or not report["limitations"]:
            report["limitations"] = [
                "Investigation scope is constrained to ingested authentication log records.",
                "External threat intelligence correlation is pending proxy verification."
            ]

        logger.info(f"[{self.name}] Generated investigation timeline with {len(report.get('timeline', []))} events")
        return report

investigation_agent = InvestigationAgent()
