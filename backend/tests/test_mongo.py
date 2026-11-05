import sys
import asyncio
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.services.mongo_service import mongo_service

async def test():
    print("Testing mongo_service connect...")
    await mongo_service.connect()
    print("Connected:", mongo_service.is_connected, "is_mock:", mongo_service.is_mock)
    health = await mongo_service.check_health()
    print("Mongo health:", health)

if __name__ == "__main__":
    asyncio.run(test())
