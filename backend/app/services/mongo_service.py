import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
# pyrefly: ignore[missing-import]
import pymongo
# pyrefly: ignore[missing-import]
import mongomock
from app.config import settings

logger = logging.getLogger(__name__)

class MongoService:
    def __init__(self):
        self.uri = settings.MONGODB_URI
        self.db_name = settings.MONGODB_DB_NAME
        self.client = None
        self.db = None
        self.is_connected = False
        self.is_mock = False
        self._disk_storage_dir = settings.DATA_DIR / "db_store"
        self._disk_storage_dir.mkdir(parents=True, exist_ok=True)

    async def connect(self):
        """
        Attempts to connect to the configured MongoDB instance.
        First tries the real MongoDB server (local or remote).
        Falls back to embedded JSON-backed storage only if MongoDB is unreachable.
        Reports connection mode honestly.
        """
        import asyncio
        # pyrefly: ignore[missing-import]
        import motor.motor_asyncio

        # Always try real MongoDB first (works for local and remote URIs)
        try:
            real_client = motor.motor_asyncio.AsyncIOMotorClient(
                self.uri,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000
            )
            await asyncio.wait_for(real_client.admin.command('ping'), timeout=2.0)
            self.client = real_client
            self.db = self.client[self.db_name]
            self.is_connected = True
            self.is_mock = False
            logger.info(f"Connected to MongoDB server at {self.uri} (database: {self.db_name})")
            return
        except Exception as e:
            logger.warning(f"MongoDB connection failed ({e}). Falling back to embedded JSON storage.")

        # Fallback: Embedded JSON-backed storage (not MongoDB)
        try:
            self.client = mongomock.MongoClient()
            self.db = self.client[self.db_name]
            self.is_mock = True
            self.is_connected = True
            self._load_from_disk()
            logger.info("Using embedded JSON-backed storage (MongoDB unavailable).")
        except Exception as mock_err:
            logger.error(f"Embedded storage initialization failed: {mock_err}")
            self.is_connected = False

    def _load_from_disk(self):
        """Preloads persisted collections from disk storage into mock db."""
        for coll_name in ["incidents", "events", "feedback"]:
            file_path = self._disk_storage_dir / f"{coll_name}.json"
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data and isinstance(data, list):
                        coll = self.db[coll_name]
                        coll.delete_many({})
                        coll.insert_many(data)
                        logger.info(f"Loaded {len(data)} items for '{coll_name}' from persistent disk storage.")
                except Exception as ex:
                    logger.warning(f"Could not load {coll_name} from disk: {ex}")

    def _sync_to_disk(self, collection_name: str):
        """Synchronizes collection contents to disk for persistence across restarts."""
        if not self.is_mock or not self.db:
            return
        try:
            coll = self.db[collection_name]
            docs = list(coll.find({}, {"_id": 0}))
            file_path = self._disk_storage_dir / f"{collection_name}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(docs, f, indent=2, default=str)
        except Exception as ex:
            logger.error(f"Error syncing {collection_name} to disk: {ex}")

    # ------------------ Incidents Collection ------------------

    async def save_incident(self, incident: Dict[str, Any]) -> str:
        if not self.is_connected:
            await self.connect()
        inc = {k: v for k, v in incident.items() if k != "_id"}
        if self.is_mock:
            self.db.incidents.update_one(
                {"incident_id": inc["incident_id"]},
                {"$set": inc},
                upsert=True
            )
            self._sync_to_disk("incidents")
        else:
            await self.db.incidents.update_one(
                {"incident_id": inc["incident_id"]},
                {"$set": inc},
                upsert=True
            )
        return inc["incident_id"]

    async def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        if not self.is_connected:
            await self.connect()
        if self.is_mock:
            return self.db.incidents.find_one({"incident_id": incident_id}, {"_id": 0})
        else:
            return await self.db.incidents.find_one({"incident_id": incident_id}, {"_id": 0})

    async def list_incidents(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        if not self.is_connected:
            await self.connect()
        query: Dict[str, Any] = {}
        if severity and severity.lower() != "all":
            query["severity"] = severity.capitalize()
        if status and status.lower() != "all":
            query["status"] = status.lower()

        if self.is_mock:
            cursor = self.db.incidents.find(query, {"_id": 0}).sort("created_at", pymongo.DESCENDING).skip(skip).limit(limit)
            return list(cursor)
        else:
            cursor = self.db.incidents.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
            return await cursor.to_list(length=limit)

    async def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> bool:
        if not self.is_connected:
            await self.connect()
        if self.is_mock:
            res = self.db.incidents.update_one(
                {"incident_id": incident_id},
                {"$set": updates}
            )
            self._sync_to_disk("incidents")
            return res.modified_count > 0 or res.matched_count > 0
        else:
            res = await self.db.incidents.update_one(
                {"incident_id": incident_id},
                {"$set": updates}
            )
            return res.modified_count > 0 or res.matched_count > 0

    # ------------------ Events Collection ------------------

    async def save_events(self, events: List[Dict[str, Any]]) -> int:
        if not self.is_connected:
            await self.connect()
        if not events:
            return 0
        clean_events = [{k: v for k, v in e.items() if k != "_id"} for e in events]
        if self.is_mock:
            for e in clean_events:
                self.db.events.update_one(
                    {"event_id": e["event_id"]},
                    {"$set": e},
                    upsert=True
                )
            self._sync_to_disk("events")
        else:
            for e in clean_events:
                await self.db.events.update_one(
                    {"event_id": e["event_id"]},
                    {"$set": e},
                    upsert=True
                )
        return len(clean_events)

    async def get_events_by_incident(self, incident_id: str) -> List[Dict[str, Any]]:
        if not self.is_connected:
            await self.connect()
        if self.is_mock:
            cursor = self.db.events.find({"incident_id": incident_id}, {"_id": 0}).sort("timestamp", pymongo.ASCENDING)
            return list(cursor)
        else:
            cursor = self.db.events.find({"incident_id": incident_id}, {"_id": 0}).sort("timestamp", 1)
            return await cursor.to_list(length=500)

    # ------------------ Feedback Collection ------------------

    async def save_feedback(self, feedback: Dict[str, Any]) -> str:
        if not self.is_connected:
            await self.connect()
        clean = {k: v for k, v in feedback.items() if k != "_id"}
        if self.is_mock:
            self.db.feedback.update_one(
                {"incident_id": clean["incident_id"]},
                {"$set": clean},
                upsert=True
            )
            self._sync_to_disk("feedback")
        else:
            await self.db.feedback.update_one(
                {"incident_id": clean["incident_id"]},
                {"$set": clean},
                upsert=True
            )
        await self.update_incident(clean["incident_id"], {"status": "confirmed"})
        return clean.get("feedback_id", clean["incident_id"])

    async def get_feedback_by_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        if not self.is_connected:
            await self.connect()
        if self.is_mock:
            return self.db.feedback.find_one({"incident_id": incident_id}, {"_id": 0})
        else:
            return await self.db.feedback.find_one({"incident_id": incident_id}, {"_id": 0})

    # ------------------ Analytics ------------------

    async def get_analytics(self) -> Dict[str, Any]:
        if not self.is_connected:
            await self.connect()

        if self.is_mock:
            incidents = list(self.db.incidents.find({}, {"_id": 0}))
            feedback_list = list(self.db.feedback.find({}, {"_id": 0}))
        else:
            incidents = await self.db.incidents.find({}, {"_id": 0}).to_list(length=1000)
            feedback_list = await self.db.feedback.find({}, {"_id": 0}).to_list(length=1000)

        total_incidents = len(incidents)
        critical_count = sum(1 for i in incidents if i.get("severity") == "Critical")
        high_count = sum(1 for i in incidents if i.get("severity") == "High")
        medium_count = sum(1 for i in incidents if i.get("severity") == "Medium")
        low_count = sum(1 for i in incidents if i.get("severity") == "Low")

        # Memory operations (verified from real incident & feedback documents)
        memory_recalled_count = sum(
            1 for i in incidents
            if i.get("memory_used") is True
            and i.get("hindsight_status") == "recalled"
            and len(i.get("retrieved_memories", [])) > 0
        )
        memory_retained_count = sum(
            1 for fb in feedback_list
            if fb.get("retention_status") in ("succeeded", "retained")
            or (fb.get("retention_details") and fb.get("retention_details", {}).get("success") is True)
        )
        confirmed_count = len(feedback_list)

        # Defensive recommendations breakdown
        total_recommendations = sum(len(i.get("recommendations", [])) for i in incidents)
        total_accepted = sum(len(fb.get("accepted_recommendations", [])) for fb in feedback_list)
        total_rejected = sum(len(fb.get("rejected_recommendations", [])) for fb in feedback_list)
        total_reviewed = total_accepted + total_rejected
        total_pending = max(0, total_recommendations - total_reviewed)

        # Acceptance rate: (Accepted / Total Reviewed) * 100
        # If no recommendations have been reviewed, return None (displayed as "N/A" on dashboard)
        acceptance_rate = round((total_accepted / total_reviewed * 100), 1) if total_reviewed > 0 else None
        acceptance_rate_display = f"{acceptance_rate}%" if acceptance_rate is not None else "N/A"

        # Agent execution counts aggregated across real investigations
        agent_execution_stats = {
            "detection": {"total": 0, "completed": 0, "failed": 0},
            "investigation": {"total": 0, "completed": 0, "failed": 0},
            "memory": {"total": 0, "completed": 0, "failed": 0},
            "response": {"total": 0, "completed": 0, "failed": 0},
            "learning": {"total": len(feedback_list), "completed": memory_retained_count, "failed": len(feedback_list) - memory_retained_count}
        }
        for inc in incidents:
            ag_exec = inc.get("agent_execution", {})
            for key in ["detection", "investigation", "memory", "response"]:
                if key in ag_exec:
                    agent_execution_stats[key]["total"] += 1
                    status_val = ag_exec[key].get("status")
                    if status_val == "completed":
                        agent_execution_stats[key]["completed"] += 1
                    elif status_val == "failed":
                        agent_execution_stats[key]["failed"] += 1

        return {
            "total_incidents": total_incidents,
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count,
            "low_count": low_count,
            "confirmed_count": confirmed_count,
            "memory_assisted_count": memory_recalled_count,
            "memory_recalled_count": memory_recalled_count,
            "memory_retained_count": memory_retained_count,
            "total_recommendations": total_recommendations,
            "total_recommendations_accepted": total_accepted,
            "total_recommendations_rejected": total_rejected,
            "total_recommendations_pending": total_pending,
            "total_recommendations_reviewed": total_reviewed,
            "acceptance_rate": acceptance_rate,
            "acceptance_rate_display": acceptance_rate_display,
            "agent_execution_stats": agent_execution_stats
        }

    async def check_health(self) -> Dict[str, Any]:
        if not self.is_connected:
            await self.connect()
        if self.is_mock:
            mode = "embedded-json-storage"
            uri_display = f"file://{self._disk_storage_dir}"
        else:
            mode = "mongodb"
            uri_display = self.uri
        return {
            "status": "connected" if self.is_connected else "disconnected",
            "mode": mode,
            "database": self.db_name,
            "uri": uri_display
        }

mongo_service = MongoService()
