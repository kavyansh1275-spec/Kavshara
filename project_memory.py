from pathlib import Path
from datetime import datetime, timezone
import json

MEMORY_FILE = Path("data/projects.json")
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)


def _now():
    return datetime.now(timezone.utc).isoformat()


def _load():
    if not MEMORY_FILE.exists():
        return {}
    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save(data):
    MEMORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _key(path):
    return str(Path(path).as_posix()).strip("/") or "."


def get_project_memory(path="."):
    key = _key(path)
    data = _load()
    return {"project": key, "memory": data.get(key)}


def save_project_memory(path=".", summary="", notes="", last_task="", status="active", changed_files=None):
    key = _key(path)
    data = _load()
    existing = data.get(key, {})
    record = {
        "path": key,
        "summary": summary or existing.get("summary", ""),
        "notes": notes or existing.get("notes", ""),
        "last_task": last_task or existing.get("last_task", ""),
        "status": status or existing.get("status", "active"),
        "changed_files": changed_files if changed_files is not None else existing.get("changed_files", []),
        "updated_at": _now(),
    }
    if "created_at" not in existing:
        record["created_at"] = record["updated_at"]
    else:
        record["created_at"] = existing["created_at"]
    data[key] = record
    _save(data)
    return {"status": "saved", "memory": record}


def list_project_memory():
    data = _load()
    return {"projects": list(data.values())}


def build_project_memory_tools(registry):
    registry.register(
        "get_project_memory",
        "Load saved memory for a project. Argument: path optional.",
        get_project_memory,
    )
    registry.register(
        "save_project_memory",
        "Save project summary/task/status. Arguments: path, summary, notes, last_task, status, changed_files optional.",
        save_project_memory,
    )
    registry.register(
        "list_project_memory",
        "List saved project memory records.",
        list_project_memory,
    )
    return registry
