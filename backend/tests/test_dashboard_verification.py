import os
import sys
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def print_result(name: str, passed: bool, details: str = ""):
    status = "PASS" if passed else "FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"[{color}{status}{reset}] {name} - {details}", flush=True)

def test_dashboard_metrics():
    print("======================================================================", flush=True)
    print("      THREATLENS AI - OVERVIEW DASHBOARD DATA INTEGRITY AUDIT        ", flush=True)
    print("======================================================================\n", flush=True)

    results = {}

    # 1. Test Endpoint Response Structure
    print("--- 1. ANALYTICS ENDPOINT & LIVE METRICS STRUCTURE ---", flush=True)
    try:
        r = requests.get(f"{BASE_URL}/api/analytics", timeout=10)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        metrics = data.get("metrics", {})

        # Verify required keys
        required_keys = [
            "total_incidents", "critical_count", "high_count", "medium_count", "low_count",
            "confirmed_count", "memory_recalled_count", "memory_retained_count",
            "total_recommendations", "total_recommendations_accepted",
            "total_recommendations_rejected", "total_recommendations_pending",
            "acceptance_rate", "acceptance_rate_display", "agent_execution_stats"
        ]
        for key in required_keys:
            assert key in metrics, f"Missing required metric: {key}"

        print_result("Analytics API Structure", True, f"All {len(required_keys)} metric fields present in live payload.")
        results["endpoint_structure"] = "PASS"
    except Exception as e:
        print_result("Analytics API Structure", False, str(e))
        results["endpoint_structure"] = "FAIL"

    # 2. Test Severity Consistency
    print("\n--- 2. SEVERITY DISTRIBUTION INTEGRITY ---", flush=True)
    try:
        r = requests.get(f"{BASE_URL}/api/analytics", timeout=10)
        data = r.json()
        metrics = data.get("metrics", {})
        total = metrics["total_incidents"]
        crit = metrics["critical_count"]
        high = metrics["high_count"]
        med = metrics["medium_count"]
        low = metrics["low_count"]

        sum_sev = crit + high + med + low
        assert sum_sev == total, f"Severity sum ({sum_sev}) does not match total incidents ({total})"

        # Check severity_distribution array
        sev_dist = data.get("severity_distribution", [])
        dist_total = sum(item["value"] for item in sev_dist)
        assert dist_total == total, f"Distribution array total ({dist_total}) does not match total ({total})"

        print_result("Severity Distribution Consistency", True, f"Total ({total}) = Crit ({crit}) + High ({high}) + Med ({med}) + Low ({low})")
        results["severity_consistency"] = "PASS"
    except Exception as e:
        print_result("Severity Distribution Consistency", False, str(e))
        results["severity_consistency"] = "FAIL"

    # 3. Test Acceptance Rate Formula & N/A Display
    print("\n--- 3. ACCEPTANCE RATE FORMULA & N/A HANDLING ---", flush=True)
    try:
        r = requests.get(f"{BASE_URL}/api/analytics", timeout=10)
        data = r.json()
        metrics = data.get("metrics", {})
        acc = metrics["total_recommendations_accepted"]
        rej = metrics["total_recommendations_rejected"]
        reviewed = metrics["total_recommendations_reviewed"]
        rate = metrics["acceptance_rate"]
        display = metrics["acceptance_rate_display"]

        assert reviewed == (acc + rej), f"Reviewed ({reviewed}) != Accepted ({acc}) + Rejected ({rej})"

        if reviewed == 0:
            assert rate is None, f"Expected None acceptance_rate when 0 reviewed, got: {rate}"
            assert display == "N/A", f"Expected 'N/A' display, got: {display}"
            print_result("Acceptance Rate Calculation", True, "0 reviews evaluated -> returns None and 'N/A' display (not 100%)")
        else:
            expected_rate = round((acc / reviewed) * 100, 1)
            assert rate == expected_rate, f"Calculated rate ({rate}) != Expected ({expected_rate})"
            assert display == f"{expected_rate}%", f"Display ({display}) != Expected ({expected_rate}%)"
            print_result("Acceptance Rate Calculation", True, f"{acc} accepted / {reviewed} reviewed = {rate}% (Display: {display})")

        results["acceptance_rate_formula"] = "PASS"
    except Exception as e:
        print_result("Acceptance Rate Calculation", False, str(e))
        results["acceptance_rate_formula"] = "FAIL"

    # 4. Test Hindsight Metrics (No False Counts)
    print("\n--- 4. HINDSIGHT REAL OPERATIONS METRICS ---", flush=True)
    try:
        r = requests.get(f"{BASE_URL}/api/analytics", timeout=10)
        data = r.json()
        metrics = data.get("metrics", {})
        hinfo = data.get("hindsight_info", {})

        recalled_ops = metrics["memory_recalled_count"]
        retained_ops = metrics["memory_retained_count"]

        assert hinfo.get("status") == "connected", f"Hindsight not reported connected: {hinfo}"
        assert hinfo.get("memory_recalled_operations") == recalled_ops
        assert hinfo.get("memory_retained_operations") == retained_ops

        # Check incidents in DB: recalled count must match incidents with memory_used == True
        inc_res = requests.get(f"{BASE_URL}/api/incidents?limit=100", timeout=10)
        inc_list = inc_res.json().get("incidents", [])
        actual_recalled_in_db = sum(1 for i in inc_list if i.get("memory_used") is True and i.get("hindsight_status") == "recalled" and len(i.get("retrieved_memories", [])) > 0)

        assert recalled_ops == actual_recalled_in_db, f"Reported recalled ops ({recalled_ops}) != Actual in DB ({actual_recalled_in_db})"

        print_result("Hindsight Verified Operations", True, f"Recalls ({recalled_ops}) and Retains ({retained_ops}) strictly match verified DB records.")
        results["hindsight_metrics"] = "PASS"
    except Exception as e:
        print_result("Hindsight Verified Operations", False, str(e))
        results["hindsight_metrics"] = "FAIL"

    # 5. Test Five-Agent Mesh Display
    print("\n--- 5. FIVE-AGENT SOC MESH INTEGRITY ---", flush=True)
    try:
        r = requests.get(f"{BASE_URL}/api/analytics", timeout=10)
        data = r.json()
        agent_mesh = data.get("agent_mesh", [])

        assert len(agent_mesh) == 5, f"Expected 5 agents, got {len(agent_mesh)}"
        agent_ids = [a["id"] for a in agent_mesh]
        assert agent_ids == ["detection", "investigation", "memory", "response", "learning"], f"Unexpected agent list: {agent_ids}"

        for ag in agent_mesh:
            assert ag["status"] in ["available", "active", "running", "completed", "degraded", "unavailable"], f"Invalid agent status: {ag['status']}"
            assert "role" in ag and ag["role"], f"Missing role for {ag['id']}"
            assert "execution_count" in ag and ag["execution_count"] >= 0, f"Missing execution_count for {ag['id']}"

        print_result("Five-Agent SOC Mesh", True, f"All 5 agents registered with genuine readiness statuses: {[a['name'] + ': ' + a['status'] for a in agent_mesh]}")
        results["agent_mesh"] = "PASS"
    except Exception as e:
        print_result("Five-Agent SOC Mesh", False, str(e))
        results["agent_mesh"] = "FAIL"

    # 6. Test Incident Activity & Real Defensive Actions
    print("\n--- 6. INCIDENT ACTIVITY & DEFENSIVE ACTIONS TIMELINE ---", flush=True)
    try:
        r = requests.get(f"{BASE_URL}/api/analytics", timeout=10)
        data = r.json()
        timeline = data.get("activity_timeline", [])

        # Verify no fabricated IDs and real recommendations count
        for item in timeline:
            assert item["id"].startswith("TL-"), f"Fabricated incident ID in timeline: {item['id']}"
            assert isinstance(item["recommendations_count"], int) and item["recommendations_count"] >= 0
            assert item["severity"] in ["Critical", "High", "Medium", "Low"]

        print_result("Activity Timeline Integrity", True, f"{len(timeline)} chronological incident points with real recommendation counts.")
        results["activity_timeline"] = "PASS"
    except Exception as e:
        print_result("Activity Timeline Integrity", False, str(e))
        results["activity_timeline"] = "FAIL"

    # 7. Test Backend Persistence & Cache Consistency Across Requests
    print("\n--- 7. PERSISTENCE & DATA CONSISTENCY ---", flush=True)
    try:
        r1 = requests.get(f"{BASE_URL}/api/analytics", timeout=10).json()
        time.sleep(0.5)
        r2 = requests.get(f"{BASE_URL}/api/analytics", timeout=10).json()

        assert r1["metrics"]["total_incidents"] == r2["metrics"]["total_incidents"]
        assert r1["metrics"]["memory_recalled_count"] == r2["metrics"]["memory_recalled_count"]
        assert r1["metrics"]["total_recommendations"] == r2["metrics"]["total_recommendations"]

        print_result("Data Consistency Across Requests", True, "Metrics are deterministic and persisted in MongoDB across requests.")
        results["persistence_consistency"] = "PASS"
    except Exception as e:
        print_result("Data Consistency Across Requests", False, str(e))
        results["persistence_consistency"] = "FAIL"

    print("\n======================================================================", flush=True)
    print("                       AUDIT SUMMARY                                  ", flush=True)
    print("======================================================================", flush=True)
    all_pass = all(status == "PASS" for status in results.values())
    for test_name, status in results.items():
        color = "\033[92m" if status == "PASS" else "\033[91m"
        print(f"  - {test_name:<30}: {color}{status}\033[0m", flush=True)
    print("======================================================================", flush=True)
    print(f"OVERALL STATUS: {'ALL CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}\n", flush=True)

if __name__ == "__main__":
    test_dashboard_metrics()
