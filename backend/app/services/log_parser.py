import csv
import io
import json
import uuid
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from app.utils.validation import sanitize_event_record

# Comprehensive field alias mappings for flexible dynamic log parsing
FIELD_ALIASES = {
    "timestamp": [
        "timestamp", "time", "datetime", "date", "@timestamp",
        "event_time", "eventtime", "log_time", "created_at", "utc_time"
    ],
    "source_ip": [
        "source_ip", "src_ip", "srcip", "sourceip", "client_ip",
        "clientip", "ip_address", "ip", "src", "remote_ip",
        "origin_ip", "host_ip", "caller_ip", "source_address"
    ],
    "destination_ip": [
        "destination_ip", "dest_ip", "dst_ip", "dstip", "destinationip",
        "target_ip", "server_ip", "dst", "dest", "destination_address", "host"
    ],
    "username": [
        "username", "user", "account", "user_id", "userid", "actor",
        "login", "identity", "target_user", "usr", "principal", "account_name"
    ],
    "event_type": [
        "event_type", "event", "action", "activity", "type", "category",
        "method", "command", "operation", "audit_type", "service", "protocol"
    ],
    "status": [
        "status", "result", "outcome", "state", "disposition", "success", "auth_status"
    ],
    "raw_message": [
        "raw_message", "message", "msg", "log", "description",
        "details", "raw", "info", "log_entry", "syslog"
    ]
}

# Known non-event placeholder strings that indicate empty/invalid exports
JUNK_PATTERNS = [
    re.compile(r"^no\s+data(\s+to\s+export)?$", re.IGNORECASE),
    re.compile(r"^total\s+rows?:\s*0$", re.IGNORECASE),
    re.compile(r"^null$", re.IGNORECASE),
    re.compile(r"^undefined$", re.IGNORECASE),
    re.compile(r"^none$", re.IGNORECASE),
    re.compile(r"^n/a$", re.IGNORECASE),
    re.compile(r"^\s*$", re.IGNORECASE),
]

def _resolve_field(record: Dict[str, Any], canonical_key: str, default: Any = None) -> Any:
    """Finds the first matching key in record matching the canonical key's aliases."""
    if not isinstance(record, dict):
        return default

    aliases = FIELD_ALIASES.get(canonical_key, [canonical_key])
    record_keys_lower = {str(k).lower().strip(): k for k in record.keys()}

    for alias in aliases:
        if alias in record_keys_lower:
            actual_key = record_keys_lower[alias]
            val = record[actual_key]
            if val is not None:
                val_str = str(val).strip()
                if val_str != "" and not any(p.match(val_str) for p in JUNK_PATTERNS):
                    return val_str
    return default

def _normalize_timestamp(raw_time: Optional[str]) -> str:
    """Normalizes ISO, RFC, or common datetime strings to standard ISO 8601 UTC."""
    if not raw_time or str(raw_time).strip() in ("N/A", "None", ""):
        return datetime.now(timezone.utc).isoformat()
    raw_str = str(raw_time).strip()
    try:
        dt = datetime.fromisoformat(raw_str.replace("Z", "+00:00"))
        return dt.isoformat()
    except Exception:
        pass
    for fmt in (
        "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S",
        "%b %d %H:%M:%S", "%d/%b/%Y:%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"
    ):
        try:
            return datetime.strptime(raw_str, fmt).replace(tzinfo=timezone.utc).isoformat()
        except Exception:
            continue
    return raw_str

def _is_valid_security_record(record: Dict[str, Any], resolved: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates whether a parsed record is an actual security event.
    Rejects placeholders, empty rows, and non-security records.
    Never silently converts invalid records into fake security events.
    """
    # 1. Reject if the entire record only contains a known junk placeholder
    raw_msg = resolved.get("raw_message") or ""
    if any(p.match(str(raw_msg).strip()) for p in JUNK_PATTERNS):
        return False, f"Rejected placeholder line: '{raw_msg}'"

    # 2. Check if all values in the source record are empty/None/placeholders
    non_empty_values = [
        str(v).strip() for k, v in record.items()
        if v is not None and str(v).strip() != "" and not any(p.match(str(v).strip()) for p in JUNK_PATTERNS)
    ]
    if not non_empty_values:
        return False, "Empty or all-whitespace record"

    # 3. A valid security event must have at least one recognized meaningful security field:
    # (source_ip, username, event_type/action, or recognized status)
    has_ip = bool(resolved.get("source_ip"))
    has_user = bool(resolved.get("username"))
    has_event = bool(resolved.get("event_type"))
    has_status = bool(resolved.get("status"))

    if not (has_ip or has_user or has_event or has_status):
        return False, f"Record lacks required security fields (no IP, username, event_type, or status): {str(record)[:80]}"

    return True, None

def parse_csv_logs(content_str: str) -> Tuple[List[Dict[str, Any]], int, List[str]]:
    """
    Dynamically parses CSV logs.
    Returns (valid_events, rejected_count, parsing_errors).
    Handles missing optional fields without replacing actual information with fake values.
    """
    events = []
    rejected_count = 0
    parsing_errors = []

    # Strip empty lines from content
    lines = [l for l in content_str.splitlines() if l.strip()]
    if not lines:
        return [], 0, ["CSV file contains no content"]

    # Detect delimiter: comma, semicolon, or tab
    sample_line = lines[0]
    delimiter = ","
    if ";" in sample_line and sample_line.count(";") > sample_line.count(","):
        delimiter = ";"
    elif "\t" in sample_line and sample_line.count("\t") > sample_line.count(","):
        delimiter = "\t"

    try:
        reader = csv.DictReader(io.StringIO("\n".join(lines)), delimiter=delimiter)
    except Exception as e:
        return [], len(lines), [f"CSV parse error: {str(e)}"]

    for row_idx, row in enumerate(reader, start=1):
        if not row:
            rejected_count += 1
            continue

        raw_src_ip = _resolve_field(row, "source_ip", default="")
        raw_dst_ip = _resolve_field(row, "destination_ip", default="")
        raw_user = _resolve_field(row, "username", default="")
        raw_event = _resolve_field(row, "event_type", default="")
        raw_status = _resolve_field(row, "status", default="")
        raw_msg = _resolve_field(row, "raw_message", default="")

        resolved = {
            "source_ip": raw_src_ip,
            "destination_ip": raw_dst_ip,
            "username": raw_user,
            "event_type": raw_event,
            "status": raw_status.lower() if raw_status else "",
            "raw_message": raw_msg
        }

        is_valid, reject_reason = _is_valid_security_record(row, resolved)
        if not is_valid:
            rejected_count += 1
            if len(parsing_errors) < 10:
                parsing_errors.append(f"Row {row_idx}: {reject_reason}")
            continue

        # Build clean normalized event preserving original values (NO fake 127.0.0.1 or 'unknown')
        event = {
            "event_id": str(uuid.uuid4())[:8],
            "timestamp": _normalize_timestamp(_resolve_field(row, "timestamp", default="")),
            "source_ip": raw_src_ip,
            "destination_ip": raw_dst_ip,
            "username": raw_user,
            "event_type": raw_event or ("auth_attempt" if raw_status else "security_event"),
            "status": raw_status.lower() if raw_status else "unspecified",
            "raw_message": raw_msg or f"{raw_event or 'Security event'} from {raw_src_ip or 'unspecified'} for {raw_user or 'unspecified'}: {raw_status or 'logged'}"
        }
        events.append(sanitize_event_record(event))

    return events, rejected_count, parsing_errors

def parse_json_logs(content_str: str) -> Tuple[List[Dict[str, Any]], int, List[str]]:
    """
    Dynamically parses JSON logs (array or object containing event list).
    Returns (valid_events, rejected_count, parsing_errors).
    """
    events = []
    rejected_count = 0
    parsing_errors = []

    try:
        data = json.loads(content_str)
    except Exception as e:
        return [], 1, [f"Invalid JSON syntax: {str(e)}"]

    raw_list = []
    if isinstance(data, list):
        raw_list = data
    elif isinstance(data, dict):
        for candidate_key in ("events", "logs", "records", "data", "items"):
            if candidate_key in data and isinstance(data[candidate_key], list):
                raw_list = data[candidate_key]
                break
        else:
            raw_list = [data]
    else:
        return [], 1, ["Expected JSON list or object with event array"]

    for item_idx, item in enumerate(raw_list, start=1):
        if not isinstance(item, dict):
            rejected_count += 1
            parsing_errors.append(f"Item {item_idx}: Not a valid JSON object")
            continue

        raw_src_ip = _resolve_field(item, "source_ip", default="")
        raw_dst_ip = _resolve_field(item, "destination_ip", default="")
        raw_user = _resolve_field(item, "username", default="")
        raw_event = _resolve_field(item, "event_type", default="")
        raw_status = _resolve_field(item, "status", default="")
        raw_msg = _resolve_field(item, "raw_message", default="")

        resolved = {
            "source_ip": raw_src_ip,
            "destination_ip": raw_dst_ip,
            "username": raw_user,
            "event_type": raw_event,
            "status": raw_status.lower() if raw_status else "",
            "raw_message": raw_msg
        }

        is_valid, reject_reason = _is_valid_security_record(item, resolved)
        if not is_valid:
            rejected_count += 1
            if len(parsing_errors) < 10:
                parsing_errors.append(f"Item {item_idx}: {reject_reason}")
            continue

        event = {
            "event_id": str(item.get("event_id") or uuid.uuid4())[:8],
            "timestamp": _normalize_timestamp(_resolve_field(item, "timestamp", default="")),
            "source_ip": raw_src_ip,
            "destination_ip": raw_dst_ip,
            "username": raw_user,
            "event_type": raw_event or ("auth_attempt" if raw_status else "security_event"),
            "status": raw_status.lower() if raw_status else "unspecified",
            "raw_message": raw_msg or f"{raw_event or 'Security event'} from {raw_src_ip or 'unspecified'} for {raw_user or 'unspecified'}: {raw_status or 'logged'}"
        }
        events.append(sanitize_event_record(event))

    return events, rejected_count, parsing_errors

def parse_security_logs(filename: str, content_bytes: bytes) -> Tuple[List[Dict[str, Any]], int, List[str], str]:
    """
    Parses and normalizes security logs from file upload.
    Returns (valid_events, rejected_count, parsing_errors, detected_format).
    """
    content_str = content_bytes.decode("utf-8", errors="replace").strip()
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == ".json" or content_str.startswith("[") or content_str.startswith("{"):
        try:
            events, rejected, errors = parse_json_logs(content_str)
            return events, rejected, errors, "json"
        except Exception as e:
            if ext == ".csv":
                events, rejected, errors = parse_csv_logs(content_str)
                return events, rejected, errors, "csv"
            return [], 1, [f"Failed to parse JSON logs: {str(e)}"], "json"
    else:
        events, rejected, errors = parse_csv_logs(content_str)
        return events, rejected, errors, "csv"
