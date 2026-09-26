"""Kavshara V11-V20 foundations.

These tools extend Kavshara without granting unrestricted shell access, hidden microphone
access, or arbitrary destructive actions.
"""
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

DATA = Path("data")
DATA.mkdir(parents=True, exist_ok=True)

VERSION = "20.0-foundation"

def _json_path(name):
    return DATA / name

def _load(name, default):
    path = _json_path(name)
    try:
        value = json.loads(path.read_text(encoding="utf-8")) if path.exists() else default
        return value
    except (OSError, json.JSONDecodeError):
        return default

def _save(name, value):
    path = _json_path(name)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


VERSION_ROADMAP = {
    "V11": "Controlled Windows desktop gateway and application access",
    "V12": "Advanced research and knowledge base",
    "V13": "Automation and workflows",
    "V14": "Project and version management",
    "V15": "Specialized skills",
    "V16": "Unified memory and knowledge graph",
    "V17": "Local/cloud model routing foundation",
    "V18": "Advanced coding and editing orchestration",
    "V19": "Integrated personal workspace",
    "V20": "Kavshara OS foundation",
}

def kavshara_version():
    return {"version": VERSION, "roadmap": VERSION_ROADMAP}

def create_workflow(name, steps=None):
    name = str(name or "").strip()
    if not name:
        return {"error": "Workflow name is required."}
    workflows = _load("workflows.json", {})
    workflow_id = uuid.uuid4().hex[:10]
    workflows[workflow_id] = {
        "id": workflow_id,
        "name": name,
        "steps": steps if isinstance(steps, list) else [],
        "enabled": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _save("workflows.json", workflows)
    return {"status": "created", "workflow": workflows[workflow_id]}

def list_workflows():
    workflows = _load("workflows.json", {})
    return {"workflows": list(workflows.values())}

def set_workflow_enabled(workflow_id, enabled):
    workflows = _load("workflows.json", {})
    if workflow_id not in workflows:
        return {"error": "Workflow not found."}
    workflows[workflow_id]["enabled"] = bool(enabled)
    _save("workflows.json", workflows)
    return {"status": "updated", "workflow": workflows[workflow_id]}

def create_project_version(project, label="", notes=""):
    versions = _load("project_versions.json", {})
    key = str(project or ".").strip()
    record = versions.setdefault(key, {"versions": []})
    next_number = len(record["versions"]) + 1
    item = {
        "version": f"v{next_number}",
        "label": label or f"Version {next_number}",
        "notes": notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    record["versions"].append(item)
    _save("project_versions.json", versions)
    return {"status": "created", "project": key, "version": item}

def list_project_versions(project):
    key = str(project or ".").strip()
    versions = _load("project_versions.json", {})
    return {"project": key, "versions": versions.get(key, {}).get("versions", [])}

def add_skill(name, description, trigger=""):
    name = re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(name or "").strip()).strip("-")
    if not name:
        return {"error": "Skill name is required."}
    skills = _load("skills.json", {})
    skills[name] = {
        "name": name,
        "description": str(description or "").strip(),
        "trigger": str(trigger or "").strip(),
        "enabled": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save("skills.json", skills)
    return {"status": "saved", "skill": skills[name]}

def list_skills():
    return {"skills": list(_load("skills.json", {}).values())}

def add_knowledge(subject, relation, object_value, source="user"):
    subject = str(subject or "").strip()
    relation = str(relation or "").strip()
    object_value = str(object_value or "").strip()
    if not subject or not relation or not object_value:
        return {"error": "subject, relation, and object are required."}
    graph = _load("knowledge_graph.json", [])
    triple = {
        "id": uuid.uuid4().hex[:12],
        "subject": subject,
        "relation": relation,
        "object": object_value,
        "source": source,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    graph.append(triple)
    _save("knowledge_graph.json", graph[-5000:])
    return {"status": "saved", "triple": triple}

def query_knowledge(query):
    query = str(query or "").strip().lower()
    graph = _load("knowledge_graph.json", [])
    matches = [
        item for item in graph
        if query in item["subject"].lower()
        or query in item["relation"].lower()
        or query in item["object"].lower()
    ]
    return {"query": query, "matches": matches[-50:]}

def model_route(task_type="general"):
    local_model = os.getenv("KAVSHARA_MODEL", "qwen2.5:3b")
    cloud_model = os.getenv("KAVSHARA_CLOUD_MODEL", "")
    use_cloud = os.getenv("KAVSHARA_ALLOW_CLOUD", "0").lower() in {"1", "true", "yes"}
    route = "local"
    model = local_model
    if use_cloud and cloud_model and task_type in {"research", "large_code", "complex"}:
        route = "cloud"
        model = cloud_model
    return {
        "route": route,
        "model": model,
        "task_type": task_type,
        "cloud_enabled": use_cloud,
        "note": "Cloud routing requires explicit KAVSHARA_ALLOW_CLOUD opt-in.",
    }

def build_advanced_tools(registry):
    registry.register("kavshara_version", "Show Kavshara V11-V20 capability roadmap and current foundation version.", kavshara_version)
    registry.register("create_workflow", "Create a disabled workflow definition. Arguments: name, steps optional.", create_workflow)
    registry.register("list_workflows", "List saved workflows.", list_workflows)
    registry.register("set_workflow_enabled", "Enable or disable a saved workflow. Arguments: workflow_id, enabled.", set_workflow_enabled)
    registry.register("create_project_version", "Create a project version record. Arguments: project, label optional, notes optional.", create_project_version)
    registry.register("list_project_versions", "List project version records. Argument: project.", list_project_versions)
    registry.register("add_skill", "Register a reusable Kavshara skill. Arguments: name, description, trigger optional.", add_skill)
    registry.register("list_skills", "List registered reusable skills.", list_skills)
    registry.register("add_knowledge", "Store a knowledge-graph triple. Arguments: subject, relation, object_value, source optional.", add_knowledge)
    registry.register("query_knowledge", "Search the local knowledge graph. Argument: query.", query_knowledge)
    registry.register("model_route", "Choose local/cloud model routing without exposing secrets. Argument: task_type.", model_route)
    return registry
