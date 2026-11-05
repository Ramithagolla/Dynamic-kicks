import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def cleanup_legacy():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["threatlens_db"]

    # Check for legacy incidents
    inc_res = await db["incidents"].delete_many({
        "$or": [
            {"incident_id": "TL-20261105-A4BC8F"},
            {"raw_message": {"$regex": "No Data to export", "$options": "i"}},
            {"title": {"$regex": "No Data to export", "$options": "i"}}
        ]
    })
    print(f"Deleted {inc_res.deleted_count} legacy incidents.")

    ev_res = await db["events"].delete_many({
        "$or": [
            {"incident_id": "TL-20261105-A4BC8F"},
            {"raw_message": {"$regex": "No Data to export", "$options": "i"}}
        ]
    })
    print(f"Deleted {ev_res.deleted_count} legacy events.")
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_legacy())
