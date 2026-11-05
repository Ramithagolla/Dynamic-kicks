from typing import Dict, Any, List

def calculate_severity(
    failed_login_count: int,
    distinct_target_users: int,
    suspicious_ips: List[str],
    has_successful_login_after_failures: bool,
    admin_targeted: bool,
    anomalous_geo: bool = False
) -> Dict[str, Any]:
    """
    Deterministic rule-based severity calculation engine.
    Produces score (0-100) and severity rating: Critical, High, Medium, Low.
    """
    score = 0
    reasons = []

    # Repeated failed logins
    if failed_login_count >= 20:
        score += 35
        reasons.append(f"High frequency authentication attack ({failed_login_count} failures)")
    elif failed_login_count >= 5:
        score += 20
        reasons.append(f"Brute-force password spray pattern ({failed_login_count} failures)")
    elif failed_login_count > 0:
        score += 10
        reasons.append(f"Multiple failed logins detected ({failed_login_count} failures)")

    # Credential stuffing across multiple users
    if distinct_target_users >= 3:
        score += 25
        reasons.append(f"Multi-account targeting ({distinct_target_users} distinct accounts)")
    elif distinct_target_users > 1:
        score += 15
        reasons.append(f"Targeting multiple accounts ({distinct_target_users} accounts)")

    # Post-failure success -> High likelihood of compromise
    if has_successful_login_after_failures:
        score += 35
        reasons.append("Account compromise indicator: Successful authentication following repeated failures")

    # High-privilege account
    if admin_targeted:
        score += 20
        reasons.append("High-privilege target (Administrator/Root/SecOps)")

    # Suspicious origin
    if suspicious_ips:
        score += 15
        reasons.append(f"Anomalous/unrecognized source IPs ({len(suspicious_ips)} unique)")

    if anomalous_geo:
        score += 15
        reasons.append("Geographic anomaly / impossible travel pattern")

    # Cap score at 100
    score = min(score, 100)

    # Determine severity label
    if score >= 80:
        severity = "Critical"
    elif score >= 55:
        severity = "High"
    elif score >= 30:
        severity = "Medium"
    else:
        severity = "Low"

    return {
        "severity": severity,
        "score": score,
        "reasons": reasons
    }
