from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Finding(BaseModel):
    title: str
    description: str
    evidence: List[str] = Field(default_factory=list)
    confidence: float = 0.95
    category: str = "Detection"

class Recommendation(BaseModel):
    id: str
    action: str
    description: str
    priority: str  # "Critical", "High", "Medium", "Low"
    rationale: str
    supporting_evidence: List[str] = Field(default_factory=list)
    requires_human_approval: bool = True
    executed: bool = False

class MemoryReference(BaseModel):
    memory_id: Optional[str] = None
    text: str
    relevance_score: Optional[float] = None
    source_incident_id: Optional[str] = None
    created_at: Optional[str] = None

class Incident(BaseModel):
    incident_id: str
    title: str
    severity: str  # "Critical", "High", "Medium", "Low"
    status: str = "open"  # "open", "investigating", "resolved", "confirmed"
    attack_type: str
    indicators: List[str] = Field(default_factory=list)
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    observed_facts: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    memory_used: bool = False
    retrieved_memories: List[Dict[str, Any]] = Field(default_factory=list)
    memory_synthesis: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_count: int = 0
