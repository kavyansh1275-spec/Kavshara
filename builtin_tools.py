from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

WORKSPACE = Path("workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)


def _safe_path(relative_path):
    candidate = (WORKSPACE / relative_path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Path must stay inside Kavshara's workspace.")
    return candidate


def list_files(path="."):
    root = _safe_path(path)
    if not root.exists():
        return {"error": "Path does not exist"}
    if not root.is_dir():
        return {"error": "Path is not a directory"}
    return {
        "path": str(root.relative_to(WORKSPACE)),
        "files": [
            {"name": p.name, "type": "directory" if p.is_dir() else "file"}
            for p in sorted(root.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        ],
    }


def read_file(path):
    target = _safe_path(path)
    if not target.exists() or not target.is_file():
        return {"error": "File does not exist or is not a file"}
    text = target.read_text(encoding="utf-8")
    return {"path": str(target.relative_to(WORKSPACE)), "content": text[:20000], "truncated": len(text) > 20000}


def write_file(path, content):
    target = _safe_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"path": str(target.relative_to(WORKSPACE)), "bytes": target.stat().st_size, "status": "written"}



PROJECT_MEMORY_FILE = Path("data/projects.json")
SNAPSHOT_ROOT = WORKSPACE / ".kavshara" / "snapshots"
MAX_SNAPSHOT_FILE_SIZE = 5_000_000


def _load_project_memory():
    if not PROJECT_MEMORY_FILE.exists():
        return {}
    try:
        data = json.loads(PROJECT_MEMORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def get_project_memory(path="."):
    key = str(Path(path).as_posix()).strip("/") or "."
    return {"project": key, "memory": _load_project_memory().get(key)}


def save_project_memory(path=".", summary="", notes="", last_task="", status="active", changed_files=None):
    key = str(Path(path).as_posix()).strip("/") or "."
    data = _load_project_memory()
    old = data.get(key, {})
    now = datetime.now(timezone.utc).isoformat()
    record = {"path": key, "summary": summary or old.get("summary", ""), "notes": notes or old.get("notes", ""), "last_task": last_task or old.get("last_task", ""), "status": status or old.get("status", "active"), "changed_files": changed_files if changed_files is not None else old.get("changed_files", []), "created_at": old.get("created_at", now), "updated_at": now}
    data[key] = record
    PROJECT_MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROJECT_MEMORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"status": "saved", "memory": record}


def _snapshot_files(root):
    ignored = {".git", ".venv", "venv", "node_modules", "__pycache__", ".next", "dist", "build", ".idea", ".vscode", ".kavshara"}
    for path in root.rglob("*"):
        if path.is_file() and not any(part in ignored for part in path.parts):
            yield path


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_snapshot(path="."):
    root = _safe_path(path)
    if not root.is_dir():
        return {"error": "Path is not a directory."}
    snapshot_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder = SNAPSHOT_ROOT / snapshot_id
    files_root = folder / "files"
    files_root.mkdir(parents=True, exist_ok=False)
    manifest = {"snapshot_id": snapshot_id, "project": str(root.relative_to(WORKSPACE)), "files": []}
    for source in _snapshot_files(root):
        if source.stat().st_size > MAX_SNAPSHOT_FILE_SIZE:
            continue
        rel = source.relative_to(root)
        dest = files_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        manifest["files"].append({"path": rel.as_posix(), "size": source.stat().st_size, "sha256": _sha256(source)})
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"status": "created", "snapshot_id": snapshot_id, "file_count": len(manifest["files"])}


def _load_snapshot(snapshot_id):
    if not isinstance(snapshot_id, str) or snapshot_id in {"", ".", ".."} or "/" in snapshot_id or "\\\\" in snapshot_id:
        raise ValueError("Invalid snapshot id.")
    folder = SNAPSHOT_ROOT / snapshot_id
    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("Snapshot not found.")
    return folder, json.loads(manifest_path.read_text(encoding="utf-8"))


def compare_snapshot(snapshot_id, path="."):
    folder, manifest = _load_snapshot(snapshot_id)
    root = _safe_path(path)
    if str(root.relative_to(WORKSPACE)) != manifest.get("project"):
        return {"error": "Snapshot belongs to a different project path."}
    old = {x["path"]: x["sha256"] for x in manifest.get("files", [])}
    current = {p.relative_to(root).as_posix(): _sha256(p) for p in _snapshot_files(root) if p.stat().st_size <= MAX_SNAPSHOT_FILE_SIZE}
    return {"snapshot_id": snapshot_id, "added": sorted(set(current)-set(old)), "modified": sorted(p for p in set(old)&set(current) if old[p] != current[p]), "deleted": sorted(set(old)-set(current))}


def restore_snapshot(snapshot_id, path="."):
    folder, manifest = _load_snapshot(snapshot_id)
    root = _safe_path(path)
    if str(root.relative_to(WORKSPACE)) != manifest.get("project"):
        return {"error": "Snapshot belongs to a different project path."}
    restored = []
    for item in manifest.get("files", []):
        source = folder / "files" / item["path"]
        dest = root / item["path"]
        if source.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            restored.append(item["path"])
    return {"status": "restored", "snapshot_id": snapshot_id, "restored_files": restored, "extra_current_files_kept": True}

def build_default_registry():
    from tools import ToolRegistry
    from coding_tools import build_coding_tools
    from project_tools import build_project_tools
    from project_memory import build_project_memory_tools
    from snapshot_tools import build_snapshot_tools
    from validation_tools import build_validation_tools

    registry = ToolRegistry()
    registry.register("list_files", "List files/directories inside the workspace. Argument: path optional.", list_files)
    registry.register("read_file", "Read a UTF-8 text file inside the workspace. Argument: path.", read_file)
    registry.register("write_file", "Create or replace a UTF-8 text file inside the workspace. Arguments: path, content.", write_file)
    build_coding_tools(registry)
    build_project_tools(registry)
    build_project_memory_tools(registry)
    build_snapshot_tools(registry)
    build_validation_tools(registry)
    return registry
