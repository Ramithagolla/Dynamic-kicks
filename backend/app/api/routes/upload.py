import uuid
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pydantic import BaseModel
from app.services.log_parser import parse_security_logs, parse_json_logs, parse_csv_logs
from app.utils.validation import validate_file_metadata

router = APIRouter(prefix="/api/upload", tags=["Upload"])

class RawLogPayload(BaseModel):
    content: str
    format: Optional[str] = "json"  # "json" or "csv"

@router.post("")
async def upload_security_logs(
    file: Optional[UploadFile] = File(None),
    raw_content: Optional[str] = Form(None),
    format_type: Optional[str] = Form("auto")
):
    """
    Accepts CSV or JSON security logs as a file upload or raw string.
    Enforces a strict 100 MB upload limit (104857600 bytes), rejecting larger files with HTTP 413.
    Validates file format, sanitizes against prompt injection,
    and returns normalized security events alongside rejected record counts.
    """
    filename = "logs.json"
    file_size = 0
    rejected_count = 0
    parsing_errors: List[str] = []

    if file:
        filename = file.filename or "logs.json"
        content_bytes = await file.read()
        file_size = len(content_bytes)

        is_valid, err_msg, status_code = validate_file_metadata(filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=status_code or status.HTTP_400_BAD_REQUEST, detail=err_msg)

        try:
            events, rejected_count, parsing_errors, detected_format = parse_security_logs(filename, content_bytes)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Log parsing error: {str(e)}"
            )
    elif raw_content:
        content_str = raw_content.strip()
        filename = "raw_payload.json" if format_type != "csv" else "raw_payload.csv"
        content_bytes = content_str.encode("utf-8")
        file_size = len(content_bytes)

        is_valid, err_msg, status_code = validate_file_metadata(filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=status_code or status.HTTP_400_BAD_REQUEST, detail=err_msg)

        try:
            if format_type == "csv" or (format_type == "auto" and not content_str.startswith("{") and not content_str.startswith("[")):
                events, rejected_count, parsing_errors = parse_csv_logs(content_str)
                detected_format = "csv"
            else:
                events, rejected_count, parsing_errors = parse_json_logs(content_str)
                detected_format = "json"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Log parsing error: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either a security log file or raw_content must be provided."
        )

    if not events:
        detail_msg = f"No valid security events could be parsed from the provided log input ({rejected_count} record(s) rejected)."
        if parsing_errors:
            detail_msg += f" Primary rejection reason: {parsing_errors[0]}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail_msg
        )

    file_id = str(uuid.uuid4())[:8]

    return {
        "success": True,
        "file_id": file_id,
        "filename": filename,
        "file_size": file_size,
        "format": detected_format,
        "event_count": len(events),
        "rejected_count": rejected_count,
        "parsing_errors": parsing_errors[:5],
        "events": events,
        "sample": events[:3]
    }
