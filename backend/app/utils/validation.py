import re
from typing import Tuple, Optional, Any, Dict, List

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 104857600 bytes (100 MB)
ALLOWED_EXTENSIONS = {".csv", ".json"}

# Prompt injection patterns commonly embedded in untrusted log messages
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+directions", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are\s+now", re.IGNORECASE),
    re.compile(r"<\s*\|im_start\|\s*>", re.IGNORECASE),
    re.compile(r"<\s*\|im_end\|\s*>", re.IGNORECASE),
    re.compile(r"\[INST\].*?\[/INST\]", re.IGNORECASE),
    re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL),
]

def validate_file_metadata(filename: str, content_length: int) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Validates file extension and size.
    Returns (is_valid, error_message, http_status_code).
    """
    if content_length > MAX_FILE_SIZE_BYTES:
        return False, f"File exceeds maximum allowed size of 100 MB (104857600 bytes). Received: {content_length} bytes.", 413

    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{ext}'. Only CSV and JSON logs are permitted.", 400

    return True, None, None

def sanitize_untrusted_text(text: Any) -> str:
    """
    Sanitizes untrusted log text strings against prompt injection
    and strips control characters.
    """
    if not isinstance(text, str):
        text = str(text) if text is not None else ""

    sanitized = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        sanitized = pattern.sub("[REDACTED_INJECTION_ATTEMPT]", sanitized)

    # Strip null bytes and non-printable control characters
    sanitized = "".join(ch for ch in sanitized if ch.isprintable() or ch in "\n\r\t")
    return sanitized.strip()

def sanitize_event_record(event: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitizes each field of a parsed security log event record."""
    clean = {}
    for key, val in event.items():
        if isinstance(val, str):
            clean[key] = sanitize_untrusted_text(val)
        elif isinstance(val, dict):
            clean[key] = {k: sanitize_untrusted_text(v) if isinstance(v, str) else v for k, v in val.items()}
        elif isinstance(val, list):
            clean[key] = [sanitize_untrusted_text(v) if isinstance(v, str) else v for v in val]
        else:
            clean[key] = val
    return clean
