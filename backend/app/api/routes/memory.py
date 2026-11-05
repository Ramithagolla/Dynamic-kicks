from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel
from app.services.hindsight_service import hindsight_service

router = APIRouter(prefix="/api/memory", tags=["Hindsight Memory"])

class ReflectRequest(BaseModel):
    query: str
    context: Optional[str] = None

@router.get("/search")
async def search_memory(
    query: str = Query(..., description="Semantic search query across previous incident memory"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Executes actual Hindsight recall operation across the shared memory bank.
    Returns real retrieved memories and metadata without hardcoded counts or fake items.
    """
    if not query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    result = await hindsight_service.recall(query=query.strip(), max_tokens=limit * 300)
    return result

@router.post("/reflect")
async def reflect_memory(payload: ReflectRequest):
    """
    Executes actual Hindsight reflect operation to synthesize contextual reasoning
    over accumulated incident observations.
    """
    if not payload.query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    result = await hindsight_service.reflect(query=payload.query.strip(), context=payload.context)
    return result

@router.get("/list")
async def list_recent_memories(limit: int = Query(25, ge=1, le=100)):
    """Lists recent memory units directly from Hindsight memory bank."""
    return await hindsight_service.list_memories(limit=limit)

@router.get("/health")
async def check_hindsight_health():
    """Returns real Hindsight connection status, base URL, and bank ID."""
    return await hindsight_service.check_health()
