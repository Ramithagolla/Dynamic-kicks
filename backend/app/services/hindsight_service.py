import asyncio
import logging
from typing import Dict, Any, List, Optional
import hindsight_client
from hindsight_client import Hindsight
from app.config import settings

logger = logging.getLogger(__name__)

def _to_serializable(val: Any) -> Any:
    if val is None or isinstance(val, (int, float, str, bool)):
        return val
    if isinstance(val, dict):
        return {k: _to_serializable(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set)):
        return [_to_serializable(x) for x in val]
    if hasattr(val, "model_dump"):
        try:
            return val.model_dump()
        except Exception:
            pass
    if hasattr(val, "to_dict"):
        try:
            return val.to_dict()
        except Exception:
            pass
    if hasattr(val, "dict"):
        try:
            return val.dict()
        except Exception:
            pass
    if hasattr(val, "__dict__"):
        return {k: _to_serializable(v) for k, v in val.__dict__.items() if not k.startswith("_")}
    return str(val)

class HindsightService:
    def __init__(self):
        self._refresh_config()
        self.client: Optional[Hindsight] = None
        self.is_connected = False
        self.last_error: Optional[str] = None
        self._initialize_client()

    def _refresh_config(self):
        self.base_url = settings.HINDSIGHT_BASE_URL
        raw_key = settings.HINDSIGHT_API_KEY if settings.HINDSIGHT_API_KEY else ""
        self.api_key = raw_key.strip() if raw_key else None
        self.bank_id = settings.HINDSIGHT_BANK_ID

    def _initialize_client(self):
        self._refresh_config()
        if not self.api_key:
            self.client = None
            self.is_connected = False
            self.last_error = "HINDSIGHT_API_KEY not configured"
            return
        try:
            self.client = Hindsight(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=30.0
            )
            logger.info(f"Initialized Hindsight client with base_url={self.base_url}, bank_id={self.bank_id}")
        except Exception as e:
            self.last_error = str(e)
            logger.warning(f"Could not initialize Hindsight client: {e}")

    async def ensure_bank(self) -> Dict[str, Any]:
        """Ensures the threatlens-security-memory bank exists on Hindsight."""
        self._initialize_client()
        if not self.client or not self.api_key:
            return {"success": False, "error": "HINDSIGHT_API_KEY is not configured", "bank_id": self.bank_id}
        try:
            try:
                config = await asyncio.wait_for(self.client.aget_bank_config(bank_id=self.bank_id), timeout=10.0)
                self.is_connected = True
                self.last_error = None
                return {"success": True, "created": False, "bank_id": self.bank_id, "config": config}
            except Exception:
                res = await asyncio.wait_for(self.client.acreate_bank(
                    bank_id=self.bank_id,
                    name="ThreatLens Security Memory",
                    mission="Persistent memory bank for cybersecurity incident investigation, analyst confirmations, root causes, and defensive remediation efficacy."
                ), timeout=10.0)
                self.is_connected = True
                self.last_error = None
                return {"success": True, "created": True, "bank_id": self.bank_id}
        except Exception as e:
            self.last_error = str(e)
            logger.warning(f"Hindsight ensure_bank failed: {e}")
            return {"success": False, "error": str(e), "bank_id": self.bank_id}

    async def retain(
        self,
        content: str,
        context: Optional[str] = None,
        document_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Executes Hindsight retain operation.
        Stores analyst-confirmed incident facts, root causes, and accepted recommendations.
        Never simulates success.
        """
        if not self.client or not self.api_key:
            return {
                "success": False,
                "error": "HINDSIGHT_API_KEY is not configured. Memory retention requires a valid Hindsight API key.",
                "bank_id": self.bank_id,
                "retained": False
            }

        try:
            await self.ensure_bank()

            res = await asyncio.wait_for(self.client.aretain(
                bank_id=self.bank_id,
                content=content,
                context=context,
                document_id=document_id,
                metadata=metadata or {},
                tags=tags or ["threatlens", "incident-resolution"]
            ), timeout=8.0)

            success = bool(getattr(res, "success", True))
            items_count = getattr(res, "items_count", 1)
            op_id = getattr(res, "operation_id", None)

            self.is_connected = True
            self.last_error = None

            return {
                "success": success,
                "bank_id": self.bank_id,
                "items_count": items_count,
                "operation_id": op_id,
                "retained": success,
                "document_id": document_id,
                "message": f"Successfully retained confirmed knowledge into Hindsight bank '{self.bank_id}'" if success else "Hindsight retain failed"
            }
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Hindsight retain API call failed: {e}")
            return {
                "success": False,
                "error": f"Hindsight retain error: {str(e)}",
                "bank_id": self.bank_id,
                "retained": False
            }

    async def recall(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Executes Hindsight recall operation.
        Retrieves related past incident findings, confirmed root causes, and resolutions.
        Never fakes counts or memories.
        """
        if not self.client or not self.api_key:
            return {
                "success": False,
                "query": query,
                "results": [],
                "count": 0,
                "message": "No relevant historical memory found.",
                "error": "HINDSIGHT_API_KEY is not configured"
            }

        try:
            res = await asyncio.wait_for(self.client.arecall(
                bank_id=self.bank_id,
                query=query,
                tags=tags,
                max_tokens=max_tokens
            ), timeout=15.0)

            results_list = []
            raw_results = getattr(res, "results", []) or []
            for r in raw_results:
                results_list.append({
                    "id": getattr(r, "id", None),
                    "text": getattr(r, "text", ""),
                    "type": getattr(r, "type", "memory"),
                    "context": getattr(r, "context", None),
                    "document_id": getattr(r, "document_id", None),
                    "metadata": _to_serializable(getattr(r, "metadata", {})),
                    "tags": _to_serializable(getattr(r, "tags", [])),
                    "scores": _to_serializable(getattr(r, "scores", {})),
                    "occurred_start": getattr(r, "occurred_start", None)
                })

            self.is_connected = True
            self.last_error = None

            return {
                "success": True,
                "query": query,
                "bank_id": self.bank_id,
                "results": results_list,
                "count": len(results_list),
                "message": f"Retrieved {len(results_list)} memories from Hindsight" if results_list else "No relevant historical memory found."
            }
        except Exception as e:
            self.last_error = str(e)
            logger.warning(f"Hindsight recall API call failed: {e}")
            return {
                "success": False,
                "query": query,
                "bank_id": self.bank_id,
                "results": [],
                "count": 0,
                "message": "No relevant historical memory found.",
                "error": str(e)
            }

    async def reflect(
        self,
        query: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes Hindsight reflect operation.
        Synthesizes historical knowledge and reasoning across accumulated observations.
        """
        if not self.client or not self.api_key:
            return {
                "success": False,
                "query": query,
                "synthesis": None,
                "based_on": [],
                "count": 0,
                "error": "HINDSIGHT_API_KEY is not configured"
            }

        try:
            res = await asyncio.wait_for(self.client.areflect(
                bank_id=self.bank_id,
                query=query,
                context=context,
                include_facts=True
            ), timeout=30.0)

            synth_text = getattr(res, "text", "")
            raw_based_on = getattr(res, "based_on", []) or []
            facts = []
            for f in raw_based_on:
                facts.append({
                    "id": getattr(f, "id", None),
                    "text": getattr(f, "text", ""),
                    "type": getattr(f, "type", "fact"),
                    "document_id": getattr(f, "document_id", None),
                    "metadata": _to_serializable(getattr(f, "metadata", {}))
                })

            self.is_connected = True
            self.last_error = None

            return {
                "success": True,
                "query": query,
                "bank_id": self.bank_id,
                "synthesis": synth_text,
                "based_on": facts,
                "count": len(facts)
            }
        except Exception as e:
            self.last_error = str(e)
            logger.warning(f"Hindsight reflect API call failed: {e}")
            return {
                "success": False,
                "query": query,
                "bank_id": self.bank_id,
                "synthesis": None,
                "based_on": [],
                "count": 0,
                "error": str(e)
            }

    async def list_memories(self, limit: int = 50) -> Dict[str, Any]:
        """Lists recent memory units directly from Hindsight memory bank."""
        if not self.client or not self.api_key:
            return {"success": False, "memories": [], "count": 0, "error": "HINDSIGHT_API_KEY is not configured"}
        try:
            res = await asyncio.wait_for(self.client.alist_memories(bank_id=self.bank_id, limit=limit), timeout=5.0)
            items = []
            raw_units = getattr(res, "items", getattr(res, "memory_units", []))
            for u in raw_units:
                items.append({
                    "id": getattr(u, "id", None),
                    "text": getattr(u, "text", str(u)),
                    "type": getattr(u, "type", "memory"),
                    "tags": getattr(u, "tags", []),
                    "created_at": getattr(u, "created_at", None)
                })
            return {"success": True, "memories": items, "count": len(items)}
        except Exception as e:
            safe_err = str(e)
            if self.api_key and self.api_key in safe_err:
                safe_err = safe_err.replace(self.api_key, "[REDACTED]")
            return {"success": False, "memories": [], "count": 0, "error": safe_err}

    async def check_health(self) -> Dict[str, Any]:
        """Verifies connection health to Hindsight server."""
        self._initialize_client()
        status = "disconnected"
        version_info = None

        if self.client and self.api_key:
            try:
                ver = await asyncio.wait_for(self.client.aget_version(), timeout=8.0)
                status = "connected"
                version_info = getattr(ver, "version", str(ver))
                self.is_connected = True
                self.last_error = None
            except Exception as e:
                status = "offline"
                safe_err = str(e)
                if self.api_key in safe_err:
                    safe_err = safe_err.replace(self.api_key, "[REDACTED]")
                self.last_error = safe_err
                self.is_connected = False
        else:
            status = "unconfigured"
            self.last_error = "HINDSIGHT_API_KEY not configured"

        return {
            "status": status,
            "base_url": self.base_url,
            "bank_id": self.bank_id,
            "api_key_configured": bool(self.api_key),
            "version": version_info,
            "last_error": self.last_error,
            "message": "Connected to official Hindsight API" if status == "connected" else (
                "HINDSIGHT_API_KEY not configured. Memory operations will report unconfigured."
                if status == "unconfigured" else f"Hindsight offline: {self.last_error}"
            )
        }

hindsight_service = HindsightService()
