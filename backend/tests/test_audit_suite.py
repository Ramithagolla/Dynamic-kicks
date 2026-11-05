import os
import sys
import json
import time
import io
import requests

BASE_URL = "http://127.0.0.1:8000"
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_data")

def print_result(name: str, passed: bool, details: str = ""):
    status = "PASS" if passed else "FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"[{color}{status}{reset}] {name} - {details}", flush=True)

def run_audit():
    print("======================================================================", flush=True)
    print("         THREATLENS AI - COMPREHENSIVE PIPELINE AUDIT SUITE           ", flush=True)
    print("======================================================================\n", flush=True)

    results = {}

    # 1. Health & Config Verification
    print("--- 1. HEALTH AND SERVICE CONNECTIVITY ---", flush=True)
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.json()
        assert data.get("mongodb", {}).get("status") == "connected", "MongoDB not connected"
        assert data.get("hindsight", {}).get("status") == "connected", "Hindsight not connected"
        assert data.get("groq", {}).get("status") == "connected", "Groq not connected"
        print_result("Health Check", True, f"MongoDB: {data['mongodb']['status']}, Hindsight: {data['hindsight']['status']}, Groq: {data['groq']['status']}")
        results["health_check"] = "PASS"
    except Exception as e:
        print_result("Health Check", False, str(e))
        results["health_check"] = "FAIL"

    # 2. File Upload Validation & Rejection
    print("\n--- 2. FILE UPLOAD & REJECTION ENFORCEMENT ---", flush=True)

    # 2a. Reject > 100MB (104857600 bytes)
    try:
        over_limit_bytes = io.BytesIO(b"timestamp,source_ip,username\n" + b"A" * (100 * 1024 * 1024 + 100))
        files = {"file": ("huge_security_log.csv", over_limit_bytes, "text/csv")}
        r = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=30)
        assert r.status_code == 413, f"Expected 413 Payload Too Large, got {r.status_code}: {r.text}"
        detail_msg = r.json().get("detail", "")
        assert "100 MB" in detail_msg, f"Expected '100 MB' in detail message, got: {detail_msg}"
        print_result("100MB File Limit Enforcement", True, f"HTTP 413 correctly returned: {detail_msg}")
        results["file_limit_100mb"] = "PASS"
    except Exception as e:
        print_result("100MB File Limit Enforcement", False, str(e))
        results["file_limit_100mb"] = "FAIL"

    # 2b. Reject junk placeholder file ("No Data to export")
    try:
        junk_content = b"No Data to export\n"
        files = {"file": ("corrupt_export.csv", io.BytesIO(junk_content), "text/csv")}
        r = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=10)
        assert r.status_code == 400, f"Expected 400 Bad Request, got {r.status_code}: {r.text}"
        assert "No valid security events" in r.text, f"Unexpected error body: {r.text}"
        print_result("Junk Payload Rejection", True, f"HTTP 400 returned with message: {r.json().get('detail')}")
        results["junk_rejection"] = "PASS"
    except Exception as e:
        print_result("Junk Payload Rejection", False, str(e))
        results["junk_rejection"] = "FAIL"

    # 3. Incident 1: Credential Attack Investigation & Feedback
    print("\n--- 3. INCIDENT 1: CREDENTIAL ATTACK INVESTIGATION & RETENTION ---", flush=True)
    inc1_id = None
    try:
        inc1_path = os.path.join(SAMPLE_DIR, "incident_1_credential_attack.csv")
        with open(inc1_path, "rb") as f:
            files = {"file": ("incident_1_credential_attack.csv", f, "text/csv")}
            up_res = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=30)
        assert up_res.status_code == 200, f"Upload 1 failed: {up_res.status_code} {up_res.text}"
        up_data1 = up_res.json()
        assert up_data1["event_count"] == 8, f"Expected 8 events, got {up_data1['event_count']}"
        assert up_data1["rejected_count"] == 0, f"Expected 0 rejected, got {up_data1['rejected_count']}"

        inv_res = requests.post(f"{BASE_URL}/api/investigate", json={"events": up_data1["events"], "title": "Incident 1: Credential Attack"}, timeout=60)
        assert inv_res.status_code == 200, f"Investigation 1 failed: {inv_res.status_code} {inv_res.text}"
        inv_payload1 = inv_res.json()
        pipeline_data1 = inv_payload1.get("data", {})
        incident_rec1 = pipeline_data1.get("incident", {})
        inc1_id = incident_rec1.get("incident_id") or inv_payload1.get("incident_id")
        assert inc1_id and inc1_id.startswith("TL-"), f"Invalid incident_id: {inc1_id}"

        # Verify genuine values
        source_ips = incident_rec1.get("source_ips", [])
        targeted_users = incident_rec1.get("targeted_users", [])
        severity = incident_rec1.get("severity", "")
        analyzed_events = incident_rec1.get("analyzed_events_count", 0)
        suspicious_events = incident_rec1.get("suspicious_events_count", 0)

        assert "198.51.100.42" in source_ips, f"Expected 198.51.100.42 in source_ips, got: {source_ips}"
        assert "127.0.0.1" not in source_ips, f"Fabricated 127.0.0.1 found in source_ips: {source_ips}"
        assert any("admin_sarah" in u for u in targeted_users), f"admin_sarah not in targeted_users: {targeted_users}"
        assert "unknown" not in targeted_users, f"Fabricated 'unknown' found in targeted_users: {targeted_users}"
        assert severity in ["Critical", "High"], f"Expected Critical or High severity, got: {severity}"
        assert analyzed_events == 8, f"Expected 8 analyzed events, got {analyzed_events}"
        assert suspicious_events >= 6, f"Expected >= 6 suspicious events, got {suspicious_events}"

        # Verify agent execution statuses
        agent_exec = pipeline_data1.get("agent_execution", {})
        assert len(agent_exec) == 5, f"Expected 5 agents, found {len(agent_exec)}"
        for ag_key in ["detection", "investigation", "memory", "response"]:
            assert agent_exec[ag_key].get("status") == "completed", f"Agent {ag_key} status is {agent_exec[ag_key].get('status')}"

        print_result("Incident 1 Pipeline Analysis", True, f"ID: {inc1_id}, Severity: {severity}, Suspicious: {suspicious_events}/{analyzed_events}, IP: {source_ips}")
        results["incident_1_investigation"] = "PASS"

        # Submit Analyst Feedback & Trigger Hindsight Retain
        time.sleep(1)
        feedback_payload = {
            "finding_confirmed": True,
            "confirmed_root_cause": "External attacker executing distributed SSH brute-force and web credential stuffing from 198.51.100.42, successfully compromising admin_sarah and escalating privileges via sudo.",
            "resolution_notes": "Blocked attacker IP on border firewall, revoked active SSH/SAML sessions, rotated admin credentials and forced MFA re-enrollment.",
            "accepted_recommendations": [
                "Block IP 198.51.100.42 on perimeter firewall",
                "Reset admin_sarah credentials and revoke session tokens",
                "Enforce rate limiting on SSH and web portal endpoints"
            ],
            "rejected_recommendations": []
        }
        fb_res = requests.post(f"{BASE_URL}/api/incidents/{inc1_id}/feedback", json=feedback_payload, timeout=30)
        assert fb_res.status_code == 200, f"Feedback submission failed: {fb_res.status_code} {fb_res.text}"
        fb_data = fb_res.json()
        assert fb_data.get("retention_status") in ["retained", "success"] or fb_data.get("success") == True, f"Hindsight retain feedback returned: {fb_data}"
        print_result("Analyst Feedback & Hindsight Retain", True, f"Feedback processed: {fb_data.get('message')}")
        results["incident_1_retention"] = "PASS"

    except Exception as e:
        print_result("Incident 1 Pipeline Analysis", False, str(e))
        results["incident_1_investigation"] = "FAIL"
        results["incident_1_retention"] = "FAIL"

    # Allow Hindsight cloud bank indexing time
    print("\nWaiting 6 seconds for Hindsight cloud indexing...", flush=True)
    time.sleep(6)

    # 4. Incident 2: Credential Stuffing & Memory Recall
    print("\n--- 4. INCIDENT 2: CREDENTIAL STUFFING & HINDSIGHT RECALL ---", flush=True)
    try:
        inc2_path = os.path.join(SAMPLE_DIR, "incident_2_similar_credential_attack.csv")
        with open(inc2_path, "rb") as f:
            files = {"file": ("incident_2_similar_credential_attack.csv", f, "text/csv")}
            up2_res = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=30)
        assert up2_res.status_code == 200, f"Upload 2 failed: {up2_res.status_code} {up2_res.text}"
        up_data2 = up2_res.json()

        inv2_res = requests.post(f"{BASE_URL}/api/investigate", json={"events": up_data2["events"], "title": "Incident 2: Similar Credential Attack"}, timeout=60)
        assert inv2_res.status_code == 200, f"Investigation 2 failed: {inv2_res.status_code} {inv2_res.text}"
        inv_payload2 = inv2_res.json()
        pipeline_data2 = inv_payload2.get("data", {})
        incident_rec2 = pipeline_data2.get("incident", {})
        memory_rec2 = pipeline_data2.get("memory", {})
        inc2_id = incident_rec2.get("incident_id")

        # Verify genuine values
        source_ips2 = incident_rec2.get("source_ips", [])
        targeted_users2 = incident_rec2.get("targeted_users", [])
        assert "198.51.100.89" in source_ips2, f"Expected 198.51.100.89, got: {source_ips2}"
        assert any("admin_jordan" in u for u in targeted_users2), f"admin_jordan not in {targeted_users2}"

        # Verify Memory Recall
        hindsight_status = memory_rec2.get("hindsight_status")
        memory_used = memory_rec2.get("memory_used")
        recalled_memories = memory_rec2.get("retrieved_memories", [])

        assert hindsight_status == "recalled", f"Expected hindsight_status == 'recalled', got: {hindsight_status}"
        assert memory_used == True, f"Expected memory_used == True, got: {memory_used}"
        assert len(recalled_memories) > 0, f"Expected recalled memories, got empty: {recalled_memories}"

        print_result("Incident 2 Memory Recall", True, f"Recalled {len(recalled_memories)} memories from bank. Status: {hindsight_status}")
        results["incident_2_recall"] = "PASS"

    except Exception as e:
        print_result("Incident 2 Memory Recall", False, str(e))
        results["incident_2_recall"] = "FAIL"

    # 5. Normal Baseline Traffic Verification
    print("\n--- 5. BENIGN / BASELINE TRAFFIC INVESTIGATION ---", flush=True)
    try:
        baseline_path = os.path.join(SAMPLE_DIR, "normal_authentication_baseline.csv")
        with open(baseline_path, "rb") as f:
            files = {"file": ("normal_authentication_baseline.csv", f, "text/csv")}
            up_b_res = requests.post(f"{BASE_URL}/api/upload", files=files, timeout=30)
        assert up_b_res.status_code == 200, f"Baseline upload failed: {up_b_res.status_code} {up_b_res.text}"
        up_b_data = up_b_res.json()

        inv_b_res = requests.post(f"{BASE_URL}/api/investigate", json={"events": up_b_data["events"], "title": "Normal Authentication Baseline"}, timeout=60)
        assert inv_b_res.status_code == 200, f"Baseline investigation failed: {inv_b_res.status_code} {inv_b_res.text}"
        inv_payload_b = inv_b_res.json()
        pipeline_data_b = inv_payload_b.get("data", {})
        incident_rec_b = pipeline_data_b.get("incident", {})
        memory_rec_b = pipeline_data_b.get("memory", {})

        sev = incident_rec_b.get("severity")
        atk = incident_rec_b.get("attack_type", "")
        susp = incident_rec_b.get("suspicious_events_count", 0)
        hstatus = memory_rec_b.get("hindsight_status", "")

        assert sev == "Low", f"Expected Low severity for baseline, got: {sev}"
        assert "Baseline" in atk or "Normal" in atk, f"Expected baseline classification, got: {atk}"
        assert susp == 0, f"Expected 0 suspicious events, got: {susp}"
        assert hstatus in ["not_applicable", "no_matching_memory"], f"Expected memory not_applicable for baseline, got {hstatus}"

        print_result("Baseline Traffic Classification", True, f"Attack Type: '{atk}', Severity: {sev}, Suspicious Events: {susp}, Memory: {hstatus}")
        results["baseline_classification"] = "PASS"
    except Exception as e:
        print_result("Baseline Traffic Classification", False, str(e))
        results["baseline_classification"] = "FAIL"

    # 6. MongoDB Persistence Verification
    print("\n--- 6. MONGODB PERSISTENCE VERIFICATION ---", flush=True)
    try:
        assert inc1_id is not None
        r_get = requests.get(f"{BASE_URL}/api/incidents/{inc1_id}", timeout=10)
        assert r_get.status_code == 200, f"Failed to retrieve incident from DB: {r_get.status_code}"
        db_payload = r_get.json()
        db_inc = db_payload.get("incident", {})
        db_feedback = db_payload.get("feedback", {})
        db_events = db_payload.get("events", [])

        assert db_inc.get("incident_id") == inc1_id, f"Incident ID mismatch: {db_inc.get('incident_id')} vs {inc1_id}"
        assert len(db_events) == 8, f"Expected 8 persisted events, got: {len(db_events)}"
        assert db_feedback is not None and db_feedback.get("finding_confirmed") is True, f"Feedback missing or unconfirmed: {db_feedback}"
        print_result("MongoDB Persistence", True, f"Incident {inc1_id} verified with {len(db_events)} events and confirmed feedback in MongoDB.")
        results["mongodb_persistence"] = "PASS"
    except Exception as e:
        print_result("MongoDB Persistence", False, str(e))
        results["mongodb_persistence"] = "FAIL"

    print("\n======================================================================", flush=True)
    print("                         AUDIT SUMMARY                                ", flush=True)
    print("======================================================================", flush=True)
    all_pass = all(status == "PASS" for status in results.values())
    for test_name, status in results.items():
        color = "\033[92m" if status == "PASS" else "\033[91m"
        print(f"  - {test_name:<30}: {color}{status}\033[0m", flush=True)
    print("======================================================================", flush=True)
    print(f"OVERALL STATUS: {'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}\n", flush=True)

if __name__ == "__main__":
    run_audit()
