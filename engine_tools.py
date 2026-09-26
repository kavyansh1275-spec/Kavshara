import json
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).isoformat()


def create_engine_plan(goal, project="."):
    goal = str(goal).strip()
    if not goal:
        return {"error": "goal is required."}
    steps = [
        {"id": 1, "name": "Inspect project", "status": "pending"},
        {"id": 2, "name": "Plan implementation", "status": "pending"},
        {"id": 3, "name": "Implement changes", "status": "pending"},
        {"id": 4, "name": "Validate project", "status": "pending"},
        {"id": 5, "name": "Run relevant tests", "status": "pending"},
        {"id": 6, "name": "Fix failures", "status": "pending"},
        {"id": 7, "name": "Review changes", "status": "pending"},
        {"id": 8, "name": "Report result", "status": "pending"},
    ]
    return {
        "goal": goal,
        "project": project,
        "created_at": _now(),
        "steps": steps,
        "instruction": "Execute steps in order, but repeat validation/testing/fixing when evidence shows a failure.",
    }


def mark_engine_step(plan_json, step_id, status):
    try:
        plan = json.loads(plan_json) if isinstance(plan_json, str) else plan_json
        step_id = int(step_id)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        return {"error": f"invalid plan or step_id: {exc}"}

    valid = {"pending", "active", "completed", "blocked"}
    if status not in valid:
        return {"error": f"status must be one of {sorted(valid)}"}

    for step in plan.get("steps", []):
        if step.get("id") == step_id:
            step["status"] = status
            plan["updated_at"] = _now()
            return plan
    return {"error": "step not found."}


def build_engine_tools(registry):
    registry.register(
        "create_engine_plan",
        "Create an autonomous project-engineering plan. Arguments: goal, project optional.",
        create_engine_plan,
    )
    registry.register(
        "mark_engine_step",
        "Update an engine plan step. Arguments: plan_json, step_id, status.",
        mark_engine_step,
    )
    return registry
