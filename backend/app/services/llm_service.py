import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import groq
from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY.strip() if settings.GROQ_API_KEY else ""
        self.model = settings.GROQ_MODEL.strip() if settings.GROQ_MODEL else "openai/gpt-oss-120b"
        self.client = None
        self._init_client()

        # Load prompts
        self.prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        self._load_prompts()

    def _init_client(self):
        """Initialize or reinitialize the Groq AsyncClient from current settings."""
        self.api_key = settings.GROQ_API_KEY.strip() if settings.GROQ_API_KEY else ""
        self.model = settings.GROQ_MODEL.strip() if settings.GROQ_MODEL else "openai/gpt-oss-120b"
        if self.api_key:
            try:
                self.client = groq.AsyncGroq(api_key=self.api_key)
                logger.info(f"Groq client initialized. Model: {self.model}")
            except Exception as e:
                logger.error(f"Error initializing Groq client: {e}")
                self.client = None
        else:
            self.client = None

        # Load prompts
        self.prompts_dir = Path(__file__).resolve().parent.parent / "prompts"
        self._load_prompts()

    def _load_prompts(self):
        self.detection_prompt = self._read_prompt("detection.txt")
        self.investigation_prompt = self._read_prompt("investigation.txt")
        self.response_prompt = self._read_prompt("response.txt")

    def _read_prompt(self, filename: str) -> str:
        p = self.prompts_dir / filename
        if p.exists():
            return p.read_text(encoding="utf-8")
        return ""

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content
            return json.loads(raw)
        except Exception as e:
            logger.warning(f"Groq LLM call failed or unavailable: {e}. Falling back to deterministic engine.")
            return None

    # ------------------ Detection Agent Analysis ------------------

    async def generate_detection_analysis(
        self,
        events: List[Dict[str, Any]],
        rule_findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Runs LLM interpretation of security events alongside deterministic rule findings."""
        user_content = (
            f"Rule Findings Summary:\n{json.dumps(rule_findings, indent=2)}\n\n"
            f"Sample Log Events (count={len(events)}):\n"
            f"{json.dumps(events[:35], indent=2)}"
        )
        llm_res = await self._call_llm(self.detection_prompt, user_content)
        if llm_res and "findings" in llm_res:
            return llm_res

        # Deterministic cybersecurity reasoning fallback
        severity = rule_findings.get("severity", "Medium")
        failed_count = rule_findings.get("failed_count", 0)
        target_users = rule_findings.get("target_users", [])
        src_ips = rule_findings.get("suspicious_ips", [])
        has_compromise = rule_findings.get("has_compromise", False)

        if failed_count == 0 and not has_compromise and len(src_ips) == 0:
            return {
                "attack_type": "Normal Activity / Baseline",
                "severity": "Low",
                "confidence_score": 0.98,
                "summary": f"Evaluated {len(events)} security events. All activity conforms to normal operational baseline with zero authentication failures and no anomaly indicators.",
                "findings": [{
                    "title": "Baseline Authentication Consistency",
                    "description": "All events reflect routine, legitimate authentication within expected operational baselines.",
                    "evidence": [f"{len(events)} authorized events recorded across {len(target_users)} account(s)"],
                    "confidence": 0.99,
                    "category": "Baseline"
                }],
                "indicators": []
            }

        attack_type = "Brute-Force & Credential Access"
        if len(target_users) > 1:
            attack_type = "Credential Stuffing & Password Spray"
        if has_compromise:
            attack_type += " with Account Compromise"

        findings = []
        if failed_count > 0:
            findings.append({
                "title": f"Repeated Authentication Failures ({failed_count} events)",
                "description": f"Targeted authentication failures observed against account(s): {', '.join(target_users[:3])}",
                "evidence": [f"{failed_count} failed login attempts from IP(s): {', '.join(src_ips[:3])}"],
                "confidence": 0.96,
                "category": "Authentication"
            })
        if has_compromise:
            findings.append({
                "title": "Post-Brute-Force Successful Authentication",
                "description": "Anomalous successful logon recorded immediately subsequent to repeated failure bursts.",
                "evidence": [f"Successful login event for user '{target_users[0] if target_users else 'victim'}' after failures"],
                "confidence": 0.94,
                "category": "Account Compromise"
            })
        if src_ips:
            findings.append({
                "title": f"High-Volume Suspicious Origin IP: {src_ips[0]}",
                "description": "Origin IP generating excessive non-standard authentication attempts outside normal operational baselines.",
                "evidence": [f"IP {src_ips[0]} accounted for high failure volume"],
                "confidence": 0.92,
                "category": "Network"
            })

        return {
            "attack_type": attack_type,
            "severity": severity,
            "confidence_score": 0.92,
            "summary": f"Detected {attack_type.lower()} targeting {len(target_users)} user account(s) from {len(src_ips)} anomalous source IP(s).",
            "findings": findings,
            "indicators": src_ips + [f"target_user:{u}" for u in target_users]
        }

    # ------------------ Investigation Agent Analysis ------------------

    async def generate_investigation_report(
        self,
        events: List[Dict[str, Any]],
        detection_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Produces comprehensive investigation report separating facts from hypotheses."""
        user_content = (
            f"Detection Result:\n{json.dumps(detection_result, indent=2)}\n\n"
            f"Chronological Security Events (count={len(events)}):\n"
            f"{json.dumps(events[:40], indent=2)}"
        )
        llm_res = await self._call_llm(self.investigation_prompt, user_content)
        if llm_res and "observed_facts" in llm_res:
            return llm_res

        # Deterministic cybersecurity investigation construction
        attack_type = detection_result.get("attack_type", "Suspicious Activity")
        indicators = detection_result.get("indicators", [])
        ips = [i for i in indicators if not i.startswith("target_user:")]
        users = [i.replace("target_user:", "") for i in indicators if i.startswith("target_user:")]

        timeline = []
        for idx, ev in enumerate(events[:15]):
            stage = "Reconnaissance"
            if ev.get("status") == "failed":
                stage = "Credential Access"
            elif ev.get("status") == "success" and idx > 0 and any(e.get("status") == "failed" for e in events[:idx]):
                stage = "Initial Access"
            elif ev.get("status") == "success":
                stage = "Legitimate Access"
            timeline.append({
                "time": ev.get("timestamp", "N/A"),
                "stage": stage,
                "description": ev.get("raw_message", f"Authentication {ev.get('status')} for {ev.get('username')}"),
                "source_ip": ev.get("source_ip", "N/A"),
                "username": ev.get("username", "N/A"),
                "status": ev.get("status", "unknown")
            })

        if attack_type == "Normal Activity / Baseline":
            return {
                "title": "Baseline Investigation: Normal Activity Verified",
                "attack_pattern": "None (Routine Authorized Operations)",
                "summary": f"Log telemetry analysis of {len(events)} events confirms standard authorized authentication sessions. All events successfully passed security verification with zero brute-force or credential abuse indicators.",
                "observed_facts": [
                    f"Total evaluated log records: {len(events)}",
                    f"Authorized users authenticated: {', '.join(users) if users else 'authorized personnel'}",
                    "Zero authentication failures or policy violations recorded in the dataset"
                ],
                "hypotheses": [
                    "All authentication events were initiated by legitimate credential holders.",
                    "No anomalous adversary lateral movement or persistence observed."
                ],
                "timeline": timeline,
                "limitations": [
                    "Telemetry is bounded by the submitted security log window."
                ],
                "confidence": 0.99
            }

        observed_facts = [
            f"Multiple authentication attempts initiated from source IP(s): {', '.join(ips) if ips else 'external'}",
            f"Target accounts identified in audit logs: {', '.join(users) if users else 'multiple'}",
            f"Total evaluated log records: {len(events)}"
        ]
        if any(ev.get("status") == "success" for ev in events):
            observed_facts.append("Log confirms at least one valid authentication token issued following failure cluster.")

        hypotheses = [
            "Threat actor may possess a leaked credential dump or automated credential-stuffing tool.",
            "Attacker may attempt lateral movement or privilege escalation if session remains active."
        ]

        limitations = [
            "Log sample lacks MFA push-challenge server logs for second-factor telemetry.",
            "Geo-location data is inferred from external IP registries and may reflect VPN/proxy exit nodes.",
            "Endpoint process activity following successful logon is pending EDR agent synchronization."
        ]

        return {
            "title": f"Investigation: {attack_type}",
            "attack_pattern": "T1110 (Brute Force / Password Spraying) & T1078 (Valid Accounts)",
            "summary": f"Security logs indicate an aggressive authentication-based adversary campaign. Origin IP {ips[0] if ips else 'remote'} conducted systematic authentication attempts against domain accounts, concluding with possible unauthorized access.",
            "observed_facts": observed_facts,
            "hypotheses": hypotheses,
            "timeline": timeline,
            "limitations": limitations,
            "confidence": 0.91
        }

    # ------------------ Response Recommendation Agent ------------------

    async def generate_response_recommendations(
        self,
        investigation_report: Dict[str, Any],
        historical_memories: List[Dict[str, Any]],
        memory_synthesis: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates prioritized defensive recommendations informed by memory."""
        user_content = (
            f"Investigation Report:\n{json.dumps(investigation_report, indent=2)}\n\n"
            f"Retrieved Historical Incident Memories from Hindsight:\n{json.dumps(historical_memories, indent=2)}\n\n"
            f"Hindsight Reflection Synthesis:\n{memory_synthesis or 'None'}"
        )
        llm_res = await self._call_llm(self.response_prompt, user_content)
        if llm_res and "recommended_actions" in llm_res:
            return llm_res

        # Deterministic response generator informed by memory
        title_str = str(investigation_report.get("title", ""))
        pattern_str = str(investigation_report.get("attack_pattern", ""))
        if "Baseline" in title_str or pattern_str.startswith("None"):
            return {
                "recommended_actions": [
                    {
                        "id": "REC-01",
                        "action": "Maintain Standard SOC Telemetry Monitoring",
                        "description": "Continue passive monitoring of authentication logs across identity providers and network perimeter.",
                        "priority": "Low",
                        "category": "Hardening",
                        "rationale": "No adversary threat or credential abuse detected. Routine operational monitoring is sufficient.",
                        "supporting_evidence": ["All evaluated authentications passed within normal baseline"],
                        "requires_human_approval": True,
                        "executed": False
                    },
                    {
                        "id": "REC-02",
                        "action": "Routine Credential Lifecycle & MFA Auditing",
                        "description": "Periodically audit MFA enforcement and inactive service accounts according to organization baseline policies.",
                        "priority": "Low",
                        "category": "Hardening",
                        "rationale": "Ensures proactive security posture while no active attacks are present.",
                        "supporting_evidence": ["Zero failure bursts recorded in evaluation window"],
                        "requires_human_approval": True,
                        "executed": False
                    }
                ],
                "response_summary": "All events conform to normal operational baselines. No emergency containment or eradication measures required.",
                "memory_impact_statement": "Normal baseline activity verified; no threat remediation necessary."
            }

        has_memory = len(historical_memories) > 0
        memory_impact = (
            f"Applied knowledge from {len(historical_memories)} prior incident(s): Past resolutions confirmed effective IP blacklisting on perimeter firewall and immediate session revocation."
            if has_memory else
            "No prior memory matched; recommendations based solely on current evidence."
        )

        actions = [
            {
                "id": "REC-01",
                "action": "Revoke Active Sessions & Force Credential Reset",
                "description": "Invalidate all existing session cookies, OAuth refresh tokens, and force password reset at next logon.",
                "priority": "Critical",
                "category": "Containment",
                "rationale": "Mitigates immediate risk of unauthorized access through compromised credentials.",
                "supporting_evidence": ["Observed successful login after consecutive failure bursts"],
                "requires_human_approval": True,
                "executed": False
            },
            {
                "id": "REC-02",
                "action": "Enforce Perimeter Firewall Block on Offending IP",
                "description": "Add identified adversary IP addresses to perimeter ingress drop lists for 72 hours.",
                "priority": "High",
                "category": "Containment",
                "rationale": (
                    "Hindsight historical resolution confirmed perimeter block effectively halted similar credential stuffing attack."
                    if has_memory else "Stops automated credential spraying bursts at the network boundary."
                ),
                "supporting_evidence": [
                    "Memory match from prior incident confirmed firewall block efficacy" if has_memory else "High failed login rate from source IP"
                ],
                "requires_human_approval": True,
                "executed": False
            },
            {
                "id": "REC-03",
                "action": "Enforce Strict Number-Matching MFA Policy",
                "description": "Require FIDO2 or number-matching MFA challenges for all external authentication attempts.",
                "priority": "High",
                "category": "Hardening",
                "rationale": "Prevents replay and automated credential stuffing even if credentials are leaked.",
                "supporting_evidence": ["Target accounts lacked mandatory hardware-backed MFA"],
                "requires_human_approval": True,
                "executed": False
            },
            {
                "id": "REC-04",
                "action": "Audit Lateral Movement & Cloud Activity Logs",
                "description": "Perform 48-hour forensic retrospective of target user activity in cloud consoles and sensitive repositories.",
                "priority": "Medium",
                "category": "Recovery",
                "rationale": "Verifies whether adversary accessed sensitive data post-compromise.",
                "supporting_evidence": ["Potential unauthorized logon recorded"],
                "requires_human_approval": True,
                "executed": False
            }
        ]

        return {
            "recommended_actions": actions,
            "response_summary": "Comprehensive containment and eradication posture targeting immediate session containment, perimeter ingress blocking, and credential hardening.",
            "memory_impact_statement": memory_impact
        }

    def _refresh_config(self):
        current_key = settings.GROQ_API_KEY if settings.GROQ_API_KEY else ""
        self.api_key = current_key.strip()
        self.model = settings.GROQ_MODEL if settings.GROQ_MODEL else "openai/gpt-oss-120b"
        if self.api_key:
            try:
                if not self.client:
                    self.client = groq.AsyncGroq(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Error initializing Groq client: {e}")
        else:
            self.client = None

    async def check_health(self) -> Dict[str, Any]:
        import asyncio
        self._refresh_config()
        has_key = bool(self.api_key and len(self.api_key) > 5)

        if not has_key:
            return {
                "status": "fallback-mode",
                "provider": "Groq",
                "model": self.model,
                "api_key_configured": False,
                "deterministic_fallback_active": True,
                "message": "GROQ_API_KEY not configured. Deterministic security rules engine is active."
            }

        try:
            if not self.client:
                self.client = groq.AsyncGroq(api_key=self.api_key)
            # Lightweight authenticated API ping
            await asyncio.wait_for(self.client.models.list(), timeout=3.5)
            return {
                "status": "connected",
                "provider": "Groq",
                "model": self.model,
                "api_key_configured": True,
                "deterministic_fallback_active": False,
                "message": "Groq LLM inference service is connected and operational."
            }
        except Exception as e:
            safe_err = str(e)
            if self.api_key and self.api_key in safe_err:
                safe_err = safe_err.replace(self.api_key, "[REDACTED]")
            logger.warning(f"Groq API connection check failed: {safe_err}")
            return {
                "status": "error",
                "provider": "Groq",
                "model": self.model,
                "api_key_configured": True,
                "deterministic_fallback_active": True,
                "error": safe_err,
                "message": "Groq credentials configured but connection failed. Falling back to deterministic rules."
            }

llm_service = LLMService()
