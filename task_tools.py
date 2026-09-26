from pathlib import Path
from datetime import datetime, timezone
import json
import uuid

TASK_FILE = Path("data/tasks.json")
TASK_FILE.parent.mkdir(parents=True, exist_ok=True)

def _now():
    return datetime.now(timezone.utc).isoformat()

def _load():
    if not TASK_FILE.exists():
        return {}
    try:
        data = json.loads(TASK_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}

def _save(data):
    TASK_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def create_task(title, project=".", steps=None):
    if not isinstance(title, str) or not title.strip():
        return {"error": "title must be non-empty"}
    data = _load()
    task_id = uuid.uuid4().hex[:10]
    now = _now()
    clean_steps = []
    for step in steps or []:
        if isinstance(step, str) and step.strip():
            clean_steps.append({"title": step.strip(), "status": "pending"})
    task = {
        "id": task_id,
        "title": title.strip(),
        "project": str(project),
        "status": "active",
        "steps": clean_steps,
        "created_at": now,
        "updated_at": now,
    }
    data[task_id] = task
    _save(data)
    return {"status": "created", "task": task}

def get_task(task_id):
    task = _load().get(str(task_id))
    return {"task": task} if task else {"error": "Task not found"}

def list_tasks(project=None, status=None):
    tasks = list(_load().values())
    if project is not None:
        tasks = [t for t in tasks if t.get("project") == project]
    if status is not None:
        tasks = [t for t in tasks if t.get("status") == status]
    return {"tasks": sorted(tasks, key=lambda t: t.get("updated_at", ""), reverse=True)}

def update_task(task_id, status=None, title=None):
    data = _load()
    task = data.get(str(task_id))
    if not task:
        return {"error": "Task not found"}
    if status not in {None, "active", "completed", "blocked", "cancelled"}:
        return {"error": "Invalid status"}
    if title is not None:
        if not isinstance(title, str) or not title.strip():
            return {"error": "title must be non-empty"}
        task["title"] = title.strip()
    if status is not None:
        task["status"] = status
    task["updated_at"] = _now()
    _save(data)
    return {"status": "updated", "task": task}

def update_task_step(task_id, step_index, status):
    data = _load()
    task = data.get(str(task_id))
    if not task:
        return {"error": "Task not found"}
    if not isinstance(step_index, int) or step_index < 0 or step_index >= len(task.get("steps", [])):
        return {"error": "Invalid step index"}
    if status not in {"pending", "active", "completed", "blocked"}:
        return {"error": "Invalid step status"}
    task["steps"][step_index]["status"] = status
    task["updated_at"] = _now()
    _save(data)
    return {"status": "updated", "task": task}

def build_task_tools(registry):
    registry.register("create_task", "Create a persistent multi-step task. Arguments: title, project optional, steps optional list.", create_task)
    registry.register("get_task", "Load a task by id. Argument: task_id.", get_task)
    registry.register("list_tasks", "List persistent tasks. Arguments: project and status optional.", list_tasks)
    registry.register("update_task", "Update task title/status. Arguments: task_id, status/title optional.", update_task)
    registry.register("update_task_step", "Update one task step. Arguments: task_id, step_index, status.", update_task_step)
    return registry
