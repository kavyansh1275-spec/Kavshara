from pathlib import Path
import ast
import json

WORKSPACE = Path("workspace").resolve()
IGNORED = {".git", ".venv", "venv", "node_modules", "__pycache__", ".next", "dist", "build", ".idea", ".vscode", ".kavshara"}
MAX_FILES = 500

def _safe_path(path):
    candidate = (WORKSPACE / path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Path must stay inside Kavshara's workspace.")
    return candidate

def validate_project(path="."):
    root = _safe_path(path)
    if not root.is_dir():
        return {"error": "Project path is not a directory."}
    results = []
    for file_path in root.rglob("*"):
        if len(results) >= MAX_FILES:
            break
        if not file_path.is_file() or any(part in IGNORED for part in file_path.parts):
            continue
        suffix = file_path.suffix.lower()
        if suffix not in {".py", ".json"}:
            continue
        item = {"path": str(file_path.relative_to(WORKSPACE)), "valid": True}
        try:
            text = file_path.read_text(encoding="utf-8")
            if suffix == ".py":
                ast.parse(text, filename=str(file_path))
                item["type"] = "python"
            else:
                json.loads(text)
                item["type"] = "json"
        except (SyntaxError, json.JSONDecodeError, OSError) as exc:
            item["valid"] = False
            item["error"] = str(exc)
            item["type"] = "python" if suffix == ".py" else "json"
        results.append(item)
    failures = [x for x in results if not x["valid"]]
    return {"project": str(root.relative_to(WORKSPACE)), "scanned": len(results), "valid": not failures, "failures": failures}

def build_validation_tools(registry):
    registry.register("validate_project", "Validate Python syntax and JSON files without executing code. Argument: path optional.", validate_project)
    return registry
