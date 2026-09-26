import ast
import json
from pathlib import Path

WORKSPACE = Path("workspace").resolve()
IGNORED = {".git", ".venv", "venv", "__pycache__", "node_modules", ".next", "dist", "build", ".kavshara"}
MAX_FILES = 500


def _safe_project(path="."):
    candidate = (WORKSPACE / path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Project path must stay inside Kavshara's workspace.")
    return candidate


def _files(root):
    count = 0
    for path in root.rglob("*"):
        if count >= MAX_FILES:
            break
        if not path.is_file() or any(part in IGNORED for part in path.parts):
            continue
        count += 1
        yield path


def qa_project(path="."):
    root = _safe_project(path)
    if not root.exists():
        return {"error": "Project does not exist."}

    checks = []
    failures = []
    tested = 0

    for file in _files(root):
        rel = str(file.relative_to(WORKSPACE))
        try:
            if file.suffix == ".py":
                source = file.read_text(encoding="utf-8")
                ast.parse(source, filename=rel)
                checks.append({"file": rel, "check": "python_syntax", "status": "passed"})
                tested += 1
            elif file.suffix == ".json":
                json.loads(file.read_text(encoding="utf-8"))
                checks.append({"file": rel, "check": "json_syntax", "status": "passed"})
                tested += 1
        except (SyntaxError, json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
            item = {"file": rel, "status": "failed", "error": str(exc)}
            checks.append(item)
            failures.append(item)

    return {
        "project": str(root.relative_to(WORKSPACE)),
        "tested_files": tested,
        "failures": failures,
        "passed": not failures,
        "checks": checks,
    }


def build_qa_tools(registry):
    registry.register(
        "qa_project",
        "Run safe static QA checks for Python and JSON files without executing them. Argument: path optional.",
        qa_project,
    )
    return registry
