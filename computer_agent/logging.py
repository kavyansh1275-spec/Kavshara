import json
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path("data/computer_actions.jsonl")
SECRET_KEYS = {"password", "token", "secret", "api_key", "apikey", "authorization"}

def _sanitize(value):
    if isinstance(value, dict):
        return {k: "[REDACTED]" if k.lower() in SECRET_KEYS else _sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize(v) for v in value]
    return value

def log_action(action, tool, arguments, risk_level, confirmation, started_at,
               ended_at, success, verified, error_type=None):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "tool": tool,
        "arguments": _sanitize(arguments),
        "risk_level": risk_level,
        "confirmation": confirmation,
        "started_at": started_at,
        "ended_at": ended_at,
        "success": success,
        "verified": verified,
        "error_type": error_type,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
