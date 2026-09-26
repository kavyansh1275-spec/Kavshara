from pathlib import Path

WORKSPACE = Path("workspace").resolve()
MAX_FILE_SIZE = 1_000_000
MAX_FILES_PER_CHANGE = 20


def _safe_path(path):
    candidate = (WORKSPACE / path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Path must stay inside Kavshara's workspace.")
    return candidate


def apply_file_changes(changes):
    if not isinstance(changes, list) or not changes:
        return {"error": "changes must be a non-empty list."}
    if len(changes) > MAX_FILES_PER_CHANGE:
        return {"error": f"Too many files. Maximum is {MAX_FILES_PER_CHANGE}."}

    prepared = []
    seen = set()
    for item in changes:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("content"), str):
            return {"error": "Each change needs string path and content."}
        path = item["path"]
        if path in seen:
            return {"error": f"Duplicate path: {path}"}
        seen.add(path)
        target = _safe_path(path)
        if len(item["content"].encode("utf-8")) > MAX_FILE_SIZE:
            return {"error": f"File too large: {path}"}
        prepared.append((target, path, item["content"]))

    written = []
    try:
        for target, path, content in prepared:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            written.append(path)
    except OSError as exc:
        return {"status": "partial_failure", "written": written, "error": str(exc)}

    return {"status": "applied", "files_changed": written, "count": len(written)}


def build_editing_tools(registry):
    registry.register(
        "apply_file_changes",
        "Write multiple workspace files in one controlled operation. Argument: changes list of {path, content}.",
        apply_file_changes,
    )
    return registry
