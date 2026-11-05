import os
import sys
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.services.mongo_service import MongoService

def test_empty_state_calculations():
    # Instantiate standalone service with empty mock collections
    svc = MongoService()
    svc.is_connected = True
    svc.is_mock = True

    # We use mongomock
    import mongomock
    svc.client = mongomock.MongoClient()
    svc.db = svc.client["test_empty_db"]

    # Run get_analytics
    analytics = asyncio.run(svc.get_analytics())

    assert analytics["total_incidents"] == 0
    assert analytics["critical_count"] == 0
    assert analytics["high_count"] == 0
    assert analytics["medium_count"] == 0
    assert analytics["low_count"] == 0
    assert analytics["confirmed_count"] == 0
    assert analytics["memory_recalled_count"] == 0
    assert analytics["memory_retained_count"] == 0
    assert analytics["total_recommendations"] == 0
    assert analytics["total_recommendations_accepted"] == 0
    assert analytics["total_recommendations_rejected"] == 0
    assert analytics["total_recommendations_pending"] == 0
    assert analytics["acceptance_rate"] is None, f"Expected None, got {analytics['acceptance_rate']}"
    assert analytics["acceptance_rate_display"] == "N/A", f"Expected 'N/A', got {analytics['acceptance_rate_display']}"

    print("[PASS] Empty state unit verification: All counts 0 and acceptance_rate is None / 'N/A'")

if __name__ == "__main__":
    test_empty_state_calculations()
