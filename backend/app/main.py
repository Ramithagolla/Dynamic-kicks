import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.services.mongo_service import mongo_service
from app.services.hindsight_service import hindsight_service
from app.services.llm_service import llm_service
from app.api.routes import upload, investigations, incidents, feedback, memory, analytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ThreatLens")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ThreatLens AI SOC backend services...")
    # Initialize MongoDB connection
    await mongo_service.connect()
    # Attempt to initialize Hindsight memory bank if credentials are ready
    if settings.HINDSIGHT_API_KEY:
        await hindsight_service.ensure_bank()
    yield
    logger.info("Shutting down ThreatLens AI backend.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="ThreatLens AI: Multi-Agent Cybersecurity Intelligence & Incident Response Platform",
    lifespan=lifespan
)

# Enable CORS for frontend dashboard (supports standard and custom localhost ports)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(upload.router)
app.include_router(investigations.router)
app.include_router(incidents.router)
app.include_router(feedback.router)
app.include_router(memory.router)
app.include_router(analytics.router)

@app.get("/health", tags=["Health"])
async def get_health_status():
    """
    SOC Health Check Endpoint.
    Reports operational status for MongoDB, Hindsight Memory Bank, and Groq LLM Inference.
    """
    mongo_health = await mongo_service.check_health()
    hindsight_health = await hindsight_service.check_health()
    groq_health = await llm_service.check_health()

    overall_status = "healthy"
    if mongo_health.get("status") != "connected" and mongo_health.get("mode") != "in-memory-persistent-mock":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mongodb": mongo_health,
        "hindsight": hindsight_health,
        "groq": groq_health,
        "agents": {
            "agent_1_detection": "active",
            "agent_2_investigation": "active",
            "agent_3_memory": "active" if hindsight_health.get("status") == "connected" else "unavailable",
            "agent_4_response": "active",
            "agent_5_learning": "active" if (hindsight_health.get("status") == "connected" and mongo_health.get("status") == "connected") else "degraded"
        }
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "tagline": "Detect. Investigate. Remember. Defend.",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
