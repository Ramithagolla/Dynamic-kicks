import logging
from collections import defaultdict
from typing import List, Dict, Any
from app.services.llm_service import llm_service
from app.utils.severity import calculate_severity

logger = logging.getLogger(__name__)

class ThreatDetectionAgent:
    """
    AGENT 1: Threat Detection Agent
    Combines deterministic SIEM/SOC detection rules with LLM intelligence.
    Identifies brute-force, password spray, credential compromise, and suspicious origins.
    Never invents threat classifications when evidence is normal baseline or insufficient.
    """
    def __init__(self):
        self.name = "Threat Detection Agent"

    async def detect(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info(f"[{self.name}] Analyzing {len(events)} security events")

        if not events:
            return {
                "attack_type": "Insufficient Evidence",
                "severity": "Low",
                "confidence_score": 1.0,
                "summary": "Insufficient evidence: No security events provided for analysis.",
                "findings": [],
                "indicators": [],
                "rule_metrics": {
                    "severity": "Low",
                    "risk_score": 0,
                    "severity_reasons": ["No events to analyze"],
                    "failed_count": 0,
                    "target_users": [],
                    "suspicious_ips": [],
                    "has_compromise": False,
                    "compromised_logins_count": 0,
                    "total_event_count": 0
                }
            }

        # 1. Deterministic Security Rules Execution
        failed_attempts_by_ip = defaultdict(int)
        failed_attempts_by_user = defaultdict(int)
        user_attempts_by_ip = defaultdict(set)
        ip_attempts_by_user = defaultdict(set)
        successful_logins = []
        all_ips = set()
        all_users = set()

        for idx, ev in enumerate(events):
            ip = str(ev.get("source_ip") or "").strip()
            user = str(ev.get("username") or "").strip()
            status = str(ev.get("status") or "").lower().strip()

            if ip and ip.lower() not in ("unknown", "n/a", "none", ""):
                all_ips.add(ip)
            if user and user.lower() not in ("unknown", "n/a", "none", ""):
                all_users.add(user)

            if status in ("failed", "failure", "denied", "blocked"):
                if ip:
                    failed_attempts_by_ip[ip] += 1
                if user:
                    failed_attempts_by_user[user] += 1
                if ip and user:
                    user_attempts_by_ip[ip].add(user)
                    ip_attempts_by_user[user].add(ip)
            elif status in ("success", "successful", "allowed", "ok"):
                successful_logins.append({
                    "event_index": idx,
                    "event": ev,
                    "ip": ip,
                    "user": user,
                    "prior_failures_for_user": failed_attempts_by_user[user] if user else 0,
                    "prior_failures_from_ip": failed_attempts_by_ip[ip] if ip else 0
                })

        total_failures = sum(failed_attempts_by_ip.values())
        suspicious_ips = [
            ip for ip, cnt in failed_attempts_by_ip.items()
            if cnt >= 3 or len(user_attempts_by_ip[ip]) >= 2
        ]
        targeted_users = list(all_users)
        admin_targeted = any(
            u.lower() in ("admin", "administrator", "root", "secops", "itadmin", "service_account")
            for u in targeted_users
        )

        # Compromise detection: Successful login following repeated failures
        compromised_events = [
            s for s in successful_logins
            if s["prior_failures_for_user"] >= 2 or s["prior_failures_from_ip"] >= 3
        ]
        has_compromise = len(compromised_events) > 0

        # Calculate deterministic severity
        sev_result = calculate_severity(
            failed_login_count=total_failures,
            distinct_target_users=len(targeted_users),
            suspicious_ips=suspicious_ips,
            has_successful_login_after_failures=has_compromise,
            admin_targeted=admin_targeted
        )

        rule_findings = {
            "severity": sev_result["severity"],
            "risk_score": sev_result["score"],
            "severity_reasons": sev_result["reasons"],
            "failed_count": total_failures,
            "target_users": targeted_users,
            "suspicious_ips": suspicious_ips,
            "has_compromise": has_compromise,
            "compromised_logins_count": len(compromised_events),
            "total_event_count": len(events)
        }

        # Baseline check: If zero failures and no anomalies, classify as normal baseline without speculation
        if total_failures == 0 and not has_compromise and len(suspicious_ips) == 0:
            logger.info(f"[{self.name}] Completed: Attack='Normal Activity / Baseline', Severity='Low'")
            return {
                "attack_type": "Normal Activity / Baseline",
                "severity": "Low",
                "confidence_score": 0.98,
                "summary": f"Analyzed {len(events)} security events. All observed authentications and activities conform to normal operational baseline with zero failures or compromise indicators.",
                "findings": [
                    {
                        "title": "Baseline Authentication Consistency",
                        "description": "All events reflect routine, legitimate authentication within expected operational baselines.",
                        "evidence": [f"{len(events)} authorized events recorded across {len(targeted_users)} account(s)"],
                        "confidence": 0.99,
                        "category": "Baseline"
                    }
                ],
                "indicators": [],
                "rule_metrics": rule_findings
            }

        # 2. LLM Interpretation layer for suspicious activity
        analysis = await llm_service.generate_detection_analysis(events, rule_findings)

        # Merge deterministic accuracy with LLM interpretation
        analysis["rule_metrics"] = rule_findings
        if not analysis.get("severity"):
            analysis["severity"] = sev_result["severity"]

        logger.info(f"[{self.name}] Completed: Attack='{analysis.get('attack_type')}', Severity='{analysis.get('severity')}'")
        return analysis

detection_agent = ThreatDetectionAgent()
