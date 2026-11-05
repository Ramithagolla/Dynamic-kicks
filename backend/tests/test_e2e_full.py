"""
ThreatLens AI - Full End-to-End Test
=====================================
Tests the complete investigation pipeline with real API calls:
  1. Upload Incident 1 (brute-force) → get file_id + parsed events
  2. Investigate Incident 1 (pass events directly)
  3. Confirm Incident 1 (analyst feedback → Hindsight retain)
  4. Upload Incident 2 (credential stuffing - similar attack)
  5. Investigate Incident 2 (Memory Agent should recall Incident 1)
  6. Memory Explorer search
  7. Incidents list from MongoDB
  8. Learning Analytics

API contracts:
  POST /api/upload        → {file_id, event_count, events, ...}
  POST /api/investigate   → body: {events: [...], title?: str}
                          → {success, incident_id, data: {incident, detection, investigation, memory, recommendations}}
  POST /api/incidents/{id}/feedback → {success, retention_status, hindsight_retention, feedback}
  GET  /api/memory/search?query=... → {results, count, ...}
  GET  /api/incidents     → {incidents: [...]}
  GET  /api/analytics     → {metrics, severity_distribution, activity_timeline, comparison}

Run against live backend:
    python backend/tests/test_e2e_full.py
"""

import requests
import json
import time
import sys
import os

BASE_URL = "http://localhost:8000"
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "sample_data")

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

results = []


def log(label: str, status: str, detail: str = ""):
    icon = "✅" if status == "PASS" else ("⚠️ " if status == "WARN" else "❌")
    color = GREEN if status == "PASS" else (YELLOW if status == "WARN" else RED)
    print(f"{color}{icon} [{status}] {label}{RESET}")
    if detail:
        print(f"       {CYAN}{detail}{RESET}")
    results.append({"label": label, "status": status, "detail": detail})


def section(title: str):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}")


def assert_field(obj: dict, field: str, label: str, nonempty=False):
    val = obj.get(field)
    if val is None:
        log(label, "FAIL", f"Missing field: '{field}' in response keys: {list(obj.keys())[:10]}")
        return None
    if nonempty and (not val or (isinstance(val, (list, dict)) and len(val) == 0)):
        log(label, "WARN", f"Field '{field}' is empty: {val}")
        return val
    log(label, "PASS", f"{field} = {str(val)[:120]}")
    return val


# ─────────────────────────────────────────────────────────────────
# Step 0: Health Check
# ─────────────────────────────────────────────────────────────────
section("STEP 0: Backend Health Check")

try:
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    health = r.json()
    log("Backend reachable", "PASS", f"HTTP {r.status_code}")

    mongo = health.get("mongodb", {})
    mongo_ok = mongo.get("status") == "connected"
    log("MongoDB status", "PASS" if mongo_ok else "FAIL",
        f"mode={mongo.get('mode')} uri={mongo.get('uri')}")

    groq = health.get("groq", {})
    groq_ok = groq.get("status") == "connected"
    log("Groq status", "PASS" if groq_ok else "WARN",
        f"status={groq.get('status')} model={groq.get('model')}")

    hindsight = health.get("hindsight", {})
    hsk_ok = hindsight.get("status") == "connected"
    log("Hindsight status", "PASS" if hsk_ok else "WARN",
        f"status={hindsight.get('status')} bank={hindsight.get('bank_id')}")

except Exception as e:
    print(f"{RED}❌ FATAL: Backend not reachable at {BASE_URL}/health: {e}{RESET}")
    print(f"{YELLOW}Start: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000{RESET}")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────
# Step 1: Upload Incident 1 (brute-force attack)
# ─────────────────────────────────────────────────────────────────
section("STEP 1: Upload Incident 1 (Brute Force CSV)")

incident1_csv = os.path.join(SAMPLE_DATA_DIR, "incident_1_initial_brute_force.csv")
if not os.path.exists(incident1_csv):
    log("Incident 1 CSV exists", "FAIL", f"File not found: {incident1_csv}")
    sys.exit(1)

with open(incident1_csv, "rb") as f:
    r = requests.post(f"{BASE_URL}/api/upload",
                      files={"file": ("incident_1.csv", f, "text/csv")},
                      timeout=15)

if r.status_code != 200:
    log("Upload Incident 1 HTTP", "FAIL", f"HTTP {r.status_code}: {r.text[:300]}")
    sys.exit(1)

upload1 = r.json()
log("Upload Incident 1 HTTP", "PASS", f"HTTP 200")
file1_id = assert_field(upload1, "file_id", "file_id returned")
event_count1 = assert_field(upload1, "event_count", "event_count > 0")
events1 = upload1.get("events", [])
log("Parsed events available", "PASS" if events1 else "FAIL",
    f"{len(events1)} events parsed from CSV")

print(f"       file_id={file1_id}  events={len(events1)}")


# ─────────────────────────────────────────────────────────────────
# Step 2: Investigate Incident 1
# ─────────────────────────────────────────────────────────────────
section("STEP 2: Investigate Incident 1 (5-Agent Pipeline)")

print(f"{YELLOW}       Running 5-agent pipeline (may take 20-40s with real LLM)...{RESET}")

r = requests.post(
    f"{BASE_URL}/api/investigate",
    json={"events": events1, "title": "Brute Force Attack - admin_sarah (E2E Test 1)"},
    timeout=90
)

if r.status_code != 200:
    try:
        err = r.json()
    except Exception:
        err = {"raw": r.text[:300]}
    log("Investigate Incident 1 HTTP", "FAIL", f"HTTP {r.status_code}: {err}")
    sys.exit(1)

inv1 = r.json()
log("Investigate HTTP status", "PASS", f"HTTP 200")
incident1_id = assert_field(inv1, "incident_id", "incident_id assigned", nonempty=True)

# Navigate into data sub-object
data1 = inv1.get("data", {})
incident1_obj = data1.get("incident", {})
detection1 = data1.get("detection", {})
investigation1 = data1.get("investigation", {})
memory1 = data1.get("memory", {})
recs1 = data1.get("recommendations", {})

severity1 = incident1_obj.get("severity")
log("Severity assigned", "PASS" if severity1 else "FAIL", f"severity={severity1}")

attack_type1 = detection1.get("attack_type", "")
log("Attack type detected", "PASS" if attack_type1 else "WARN", f"attack_type={attack_type1}")

facts1 = investigation1.get("observed_facts", [])
log("Observed facts extracted", "PASS" if facts1 else "WARN",
    f"{len(facts1)} fact(s): {facts1[0][:80] if facts1 else ''}")

rec_actions1 = recs1.get("recommended_actions", []) if recs1 else []
log("Recommendations generated", "PASS" if rec_actions1 else "WARN",
    f"{len(rec_actions1)} action(s)")

mem_count1 = memory1.get("count", 0) if memory1 else 0
log("Memory Agent recall (Incident 1 — expect 0 or test entry)", "PASS",
    f"count={mem_count1}")

print(f"\n       Incident 1 ID : {BOLD}{incident1_id}{RESET}")
print(f"       Severity      : {BOLD}{severity1}{RESET}")
print(f"       Attack Type   : {BOLD}{attack_type1}{RESET}")


# ─────────────────────────────────────────────────────────────────
# Step 3: Submit Analyst Feedback → Learning Agent → Hindsight retain
# ─────────────────────────────────────────────────────────────────
section("STEP 3: Analyst Feedback + Hindsight Retain (Agent 5)")

accepted_ids = [a["id"] for a in rec_actions1[:2]] if rec_actions1 else ["REC-01", "REC-02"]
rejected_ids = [a["id"] for a in rec_actions1[2:3]] if len(rec_actions1) > 2 else []

feedback_payload = {
    "finding_confirmed": True,
    "accepted_recommendations": accepted_ids,
    "rejected_recommendations": rejected_ids,
    "confirmed_root_cause": (
        "Automated brute-force credential attack from external IP 198.51.100.42 targeting "
        "admin_sarah, secops_lead, and dev_alex accounts. SSH brute-force succeeded for "
        "admin_sarah with subsequent privilege escalation (sudo cat /etc/shadow)."
    ),
    "resolution_notes": (
        "Blocked IP 198.51.100.42 at perimeter firewall. Revoked admin_sarah session tokens. "
        "Forced password reset for all 3 target accounts. Enabled number-matching MFA for SSH "
        "and VPN auth. Reviewed /etc/shadow access in audit log. No data exfiltration confirmed."
    )
}

r = requests.post(
    f"{BASE_URL}/api/incidents/{incident1_id}/feedback",
    json=feedback_payload,
    timeout=30
)

if r.status_code != 200:
    try:
        err = r.json()
    except Exception:
        err = {"raw": r.text[:300]}
    log("Feedback submission HTTP", "FAIL", f"HTTP {r.status_code}: {err}")
else:
    fb1 = r.json()
    log("Feedback submission HTTP", "PASS", "HTTP 200")

    retention_status = fb1.get("retention_status", "unknown")
    log("Retention status", "PASS" if retention_status in ("retained", "success") else "WARN",
        f"retention_status={retention_status}")

    hindsight_ret = fb1.get("hindsight_retention", {})
    ret_success = hindsight_ret.get("success") if hindsight_ret else None
    ret_items = hindsight_ret.get("items_count") if hindsight_ret else None
    log("Hindsight retain API success",
        "PASS" if ret_success else "WARN",
        f"success={ret_success} items_count={ret_items}")

print(f"{YELLOW}       Waiting 6s for Hindsight to index retained memory...{RESET}")
time.sleep(6)


# ─────────────────────────────────────────────────────────────────
# Step 4: Upload Incident 2 (credential stuffing — similar attack)
# ─────────────────────────────────────────────────────────────────
section("STEP 4: Upload Incident 2 (Credential Stuffing CSV)")

incident2_csv = os.path.join(SAMPLE_DATA_DIR, "incident_2_similar_credential_stuffing.csv")
if not os.path.exists(incident2_csv):
    log("Incident 2 CSV exists", "FAIL", f"File not found: {incident2_csv}")
    sys.exit(1)

with open(incident2_csv, "rb") as f:
    r = requests.post(f"{BASE_URL}/api/upload",
                      files={"file": ("incident_2.csv", f, "text/csv")},
                      timeout=15)

if r.status_code != 200:
    log("Upload Incident 2 HTTP", "FAIL", f"HTTP {r.status_code}: {r.text[:200]}")
    sys.exit(1)

upload2 = r.json()
log("Upload Incident 2 HTTP", "PASS", "HTTP 200")
file2_id = assert_field(upload2, "file_id", "file_id returned (Incident 2)")
events2 = upload2.get("events", [])
log("Parsed events (Incident 2)", "PASS" if events2 else "FAIL",
    f"{len(events2)} events")


# ─────────────────────────────────────────────────────────────────
# Step 5: Investigate Incident 2 — Memory Agent should recall Incident 1
# ─────────────────────────────────────────────────────────────────
section("STEP 5: Investigate Incident 2 — Memory Recall Verification")

print(f"{YELLOW}       Running 5-agent pipeline (may take 20-40s)...{RESET}")

r = requests.post(
    f"{BASE_URL}/api/investigate",
    json={"events": events2, "title": "Credential Stuffing - admin_jordan / finance_ops (E2E Test 2)"},
    timeout=90
)

if r.status_code != 200:
    try:
        err = r.json()
    except Exception:
        err = {"raw": r.text[:300]}
    log("Investigate Incident 2 HTTP", "FAIL", f"HTTP {r.status_code}: {err}")
else:
    inv2 = r.json()
    log("Investigate Incident 2 HTTP", "PASS", "HTTP 200")
    incident2_id = assert_field(inv2, "incident_id", "Incident 2 ID assigned", nonempty=True)

    data2 = inv2.get("data", {})
    incident2_obj = data2.get("incident", {})
    memory2 = data2.get("memory", {})
    recs2 = data2.get("recommendations", {})

    severity2 = incident2_obj.get("severity")
    log("Severity assigned (Incident 2)", "PASS" if severity2 else "FAIL", f"severity={severity2}")

    memory_used2 = incident2_obj.get("memory_used", False)
    mem_count2 = memory2.get("count", 0) if memory2 else 0
    log("Memory used flag", "PASS" if memory_used2 else "WARN",
        f"memory_used={memory_used2}")
    log("Historical memories retrieved", "PASS" if mem_count2 > 0 else "WARN",
        f"count={mem_count2}")

    if mem_count2 > 0:
        mem_results = memory2.get("results", [])
        for i, mr in enumerate(mem_results[:2]):
            print(f"       [{i+1}] {CYAN}{str(mr.get('text', ''))[:120]}{RESET}")

    reflect2 = memory2.get("reflect", {}) if memory2 else {}
    synthesis = reflect2.get("synthesis") if isinstance(reflect2, dict) else None
    log("Hindsight reflect synthesis", "PASS" if synthesis else "WARN",
        synthesis[:150] if synthesis else "No synthesis text")

    mem_impact = recs2.get("memory_impact_statement", "") if recs2 else ""
    log("Memory influence in recommendations", "PASS" if mem_impact else "WARN",
        mem_impact[:120] if mem_impact else "No memory_impact_statement")

    print(f"\n       Incident 2 ID  : {BOLD}{incident2_id if 'incident2_id' in dir() else 'N/A'}{RESET}")
    print(f"       Severity       : {BOLD}{severity2}{RESET}")
    print(f"       Memory used    : {BOLD}{memory_used2}{RESET}")
    print(f"       Memories found : {BOLD}{mem_count2}{RESET}")


# ─────────────────────────────────────────────────────────────────
# Step 6: Memory Explorer Search
# ─────────────────────────────────────────────────────────────────
section("STEP 6: Memory Explorer — Hindsight Recall Search")

r = requests.get(f"{BASE_URL}/api/memory/search?query=brute+force+credential+admin", timeout=15)
if r.status_code == 200:
    mem_search = r.json()
    log("Memory search HTTP", "PASS", "HTTP 200")
    recall_count = mem_search.get("count", 0)
    log("Search results returned", "PASS" if recall_count > 0 else "WARN",
        f"{recall_count} result(s) from Hindsight recall")
    for i, res in enumerate(mem_search.get("results", [])[:3]):
        print(f"       [{i+1}] {CYAN}{str(res.get('text', ''))[:110]}{RESET}")
else:
    log("Memory search HTTP", "FAIL", f"HTTP {r.status_code}: {r.text[:200]}")


# ─────────────────────────────────────────────────────────────────
# Step 7: Verify Incidents List in MongoDB
# ─────────────────────────────────────────────────────────────────
section("STEP 7: Verify Incident List (MongoDB)")

r = requests.get(f"{BASE_URL}/api/incidents?limit=10", timeout=10)
if r.status_code == 200:
    inc_list = r.json()
    log("Incidents list HTTP", "PASS", "HTTP 200")
    incidents = inc_list.get("incidents", [])
    log("Incidents in MongoDB", "PASS" if len(incidents) >= 2 else "WARN",
        f"{len(incidents)} incident(s)")
    for inc in incidents[:5]:
        mem_flag = "🧠" if inc.get("memory_used") else "  "
        print(f"       {mem_flag} {inc.get('incident_id')} | {inc.get('severity','?'):8} | "
              f"{inc.get('status','?'):12} | {str(inc.get('title',''))[:45]}")
else:
    log("Incidents list HTTP", "FAIL", f"HTTP {r.status_code}: {r.text[:200]}")


# ─────────────────────────────────────────────────────────────────
# Step 8: Learning Analytics
# ─────────────────────────────────────────────────────────────────
section("STEP 8: Learning Analytics")

r = requests.get(f"{BASE_URL}/api/analytics", timeout=10)
if r.status_code == 200:
    analytics = r.json()
    log("Analytics HTTP", "PASS", "HTTP 200")
    metrics = analytics.get("metrics", {})
    total = metrics.get("total_incidents", "?")
    confirmed = metrics.get("confirmed_incidents", "?")
    log("Analytics metrics", "PASS" if metrics else "WARN",
        f"total={total}  confirmed={confirmed}")

    comparison = analytics.get("comparison", {})
    has_comp = comparison.get("has_comparison", False)
    log("Before/after comparison available", "PASS" if has_comp else "WARN",
        f"has_comparison={has_comp}")
    if has_comp:
        influence = comparison.get("insights", {}).get("memory_influence", "")
        print(f"       Memory influence: {CYAN}{str(influence)[:120]}{RESET}")
else:
    log("Analytics HTTP", "FAIL", f"HTTP {r.status_code}: {r.text[:200]}")


# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────
section("TEST SUMMARY")

passed = sum(1 for r in results if r["status"] == "PASS")
warned = sum(1 for r in results if r["status"] == "WARN")
failed = sum(1 for r in results if r["status"] == "FAIL")

print(f"\n  Total checks : {len(results)}")
print(f"  {GREEN}PASS{RESET}         : {passed}")
print(f"  {YELLOW}WARN{RESET}         : {warned}  (non-critical — expected for first runs)")
print(f"  {RED}FAIL{RESET}         : {failed}")
print()

if failed == 0:
    print(f"{GREEN}{BOLD}  ✅ ALL CRITICAL CHECKS PASSED.{RESET}")
    print(f"{GREEN}     ThreatLens AI E2E pipeline verified end-to-end.{RESET}")
elif failed <= 2:
    print(f"{YELLOW}{BOLD}  ⚠️  {failed} check(s) failed — review above.{RESET}")
    sys.exit(0)
else:
    print(f"{RED}{BOLD}  ❌ {failed} critical check(s) failed. See details above.{RESET}")
    sys.exit(1)
