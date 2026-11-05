import sys
import asyncio
from pathlib import Path

# Add backend to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.main import app
from httpx import AsyncClient, ASGITransport

async def main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
        print("HTTP STATUS:", resp.status_code)
        data = resp.json()
        print("APP:", data.get("app"))
        print("STATUS:", data.get("status"))
        print("MONGODB:", data.get("mongodb"))
        print("HINDSIGHT:", data.get("hindsight"))
        print("GROQ:", data.get("groq"))
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        print("HEALTH TEST PASSED!")

if __name__ == "__main__":
    asyncio.run(main())
