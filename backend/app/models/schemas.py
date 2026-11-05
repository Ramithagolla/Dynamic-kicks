from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FeedbackCreate(BaseModel):
    finding_confirmed: bool
    accepted_recommendations: List[str] = Field(default_factory=list)
    rejected_recommendations: List[str] = Field(default_factory=list)
    confirmed_root_cause: str
    resolution_notes: str

class FeedbackRecord(FeedbackCreate):
    feedback_id: str
    incident_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    retention_status: str = "pending"  # "succeeded", "failed", "pending"
    retention_details: Optional[Dict[str, Any]] = None

class InvestigateRequest(BaseModel):
    events: Optional[List[Dict[str, Any]]] = None
    file_id: Optional[str] = None
    dataset_name: Optional[str] = None
    title: Optional[str] = None

class MemorySearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class MemoryReflectRequest(BaseModel):
    query: str
    context: Optional[str] = None

class HealthStatus(BaseModel):
    status: str
    app: str
    version: str
    mongodb: Dict[str, Any]
    hindsight: Dict[str, Any]
    groq: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
