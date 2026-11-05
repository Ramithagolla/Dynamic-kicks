from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SecurityEvent(BaseModel):
    event_id: str
    incident_id: Optional[str] = None
    timestamp: str
    source_ip: str
    destination_ip: Optional[str] = "N/A"
    username: str
    event_type: str
    status: str  # e.g., "failed", "success", "suspicious", "denied"
    raw_message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SecurityEventCreate(BaseModel):
    timestamp: Optional[str] = None
    source_ip: str
    destination_ip: Optional[str] = "N/A"
    username: str
    event_type: str
    status: str
    raw_message: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None
