import sys
import asyncio
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.services.log_parser import parse_security_logs
from app.agents.coordinator import coordinator
from app.agents.learning_agent import learning_agent
from app.services.mongo_service import mongo_service
from app.services.hindsight_service import hindsight_service

async def run_pipeline_test():
    print("=== STARTING FULL MULTI-AGENT END-TO-END PIPELINE TEST ===")
    sample_dir = backend_path / "sample_data"

    # 1. First Investigation (Incident 1)
    file1 = sample_dir / "incident_1_initial_brute_force.json"
    with open(file1, "rb") as f:
        events1, _ = parse_security_logs(file1.name, f.read())
    print(f"Loaded Incident 1 events count: {len(events1)}")

    res1 = await coordinator.execute_investigation_pipeline(events=events1, title_override="Incident 1: Initial Brute Force")
    inc1 = res1["incident"]
    print(f"Incident 1 Created: ID={inc1['incident_id']}, Attack={inc1['attack_type']}, Severity={inc1['severity']}")
    print(f"Incident 1 Memory Used: {inc1['memory_used']} (Expected False before memory retained)")
    assert inc1["severity"] in ("Critical", "High"), f"Unexpected severity: {inc1['severity']}"
    assert len(inc1["recommendations"]) > 0, "No recommendations generated"
    for r in inc1["recommendations"]:
        assert r["requires_human_approval"] is True, "Human approval must be required"

    # 2. Analyst Feedback & Learning Agent (Hindsight retain)
    feedback_data = {
        "finding_confirmed": True,
        "accepted_recommendations": [r["action"] for r in inc1["recommendations"][:2]],
        "rejected_recommendations": [],
        "confirmed_root_cause": "Adversary conducted automated password spraying against domain accounts and compromised admin_sarah using weak credential pair.",
        "resolution_notes": "Implemented perimeter firewall drop rule on 198.51.100.42, invalidated all active tokens for admin_sarah, and enforced FIDO2 MFA."
    }

    learn_res = await learning_agent.learn(inc1, feedback_data)
    print(f"Learning Agent Retain Result: {learn_res['retention_status']}, details: {learn_res['details'].get('message', learn_res['details'].get('error'))}")

    # Save feedback in Mongo
    feedback_data["incident_id"] = inc1["incident_id"]
    feedback_data["retention_status"] = learn_res["retention_status"]
    await mongo_service.save_feedback(feedback_data)

    # 3. Second Investigation (Incident 2)
    file2 = sample_dir / "incident_2_similar_credential_stuffing.json"
    with open(file2, "rb") as f:
        events2, _ = parse_security_logs(file2.name, f.read())
    print(f"Loaded Incident 2 events count: {len(events2)}")

    res2 = await coordinator.execute_investigation_pipeline(events=events2, title_override="Incident 2: Similar Credential Stuffing")
    inc2 = res2["incident"]
    print(f"Incident 2 Created: ID={inc2['incident_id']}, Attack={inc2['attack_type']}, Severity={inc2['severity']}")
    print(f"Incident 2 Memory explanation: {inc2.get('memory_explanation')}")

    # 4. Check Analytics
    analytics = await mongo_service.get_analytics()
    print("Consolidated Analytics:", analytics)
    print("=== PIPELINE TEST COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    asyncio.run(run_pipeline_test())
