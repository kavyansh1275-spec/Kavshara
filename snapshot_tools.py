from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

WORKSPACE = Path("workspace").resolve()
SNAPSHOT_ROOT = WORKSPACE / ".kavshara" / "snapshots"
MAX_FILE_SIZE = 5_000_000
IGNORED_DIRS = {".git", ".hg", ".svn", "__pycache__", ".venv", "venv", "node_modules", ".next", "dist", "build", ".idea", ".vscode", ".kavshara"}


def _safe_path(path):
    candidate = (WORKSPACE / path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Path must stay inside Kavshara's workspace.")
    return candidate


def _iter_files(root):
    for path in root.rglob("*"):
        if path.is_file() and not any(part in IGNORED_DIRS for part in path.parts):
            yield path


def _hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_snapshot(path="."):
    root = _safe_path(path)
    if not root.is_dir():
        return {"error": "Path is not a directory."}
    snapshot_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = SNAPSHOT_ROOT / snapshot_id / "files"
    target.mkdir(parents=True, exist_ok=False)
    manifest = {"snapshot_id": snapshot_id, "project": str(root.relative_to(WORKSPACE)), "files": []}
    for source in _iter_files(root):
        if source.stat().st_size > MAX_FILE_SIZE:
            continue
        rel = source.relative_to(root)
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        manifest["files"].append({"path": rel.as_posix(), "size": source.stat().st_size, "sha256": _hash(source)})
    manifest_path = target.parent / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"status": "created", "snapshot_id": snapshot_id, "project": manifest["project"], "file_count": len(manifest["files"])}


def _load_snapshot(snapshot_id):
    if not isinstance(snapshot_id, str) or "/" in snapshot_id or "\\" in snapshot_id or snapshot_id in {"", ".", ".."}:
        raise ValueError("Invalid snapshot id.")
    folder = SNAPSHOT_ROOT / snapshot_id
    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        raise ValueError("Snapshot not found.")
    return folder, json.loads(manifest_path.read_text(encoding="utf-8"))


def list_snapshots(path="."):
    project = str(_safe_path(path).relative_to(WORKSPACE))
    if not SNAPSHOT_ROOT.exists():
        return {"snapshots": []}
    result = []
    for folder in sorted(SNAPSHOT_ROOT.iterdir(), reverse=True):
        manifest_path = folder / "manifest.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if manifest.get("project") == project:
            result.append({"snapshot_id": manifest.get("snapshot_id"), "file_count": len(manifest.get("files", []))})
    return {"snapshots": result}


def compare_snapshot(snapshot_id, path="."):
    folder, manifest = _load_snapshot(snapshot_id)
    root = _safe_path(path)
    if str(root.relative_to(WORKSPACE)) != manifest.get("project"):
        return {"error": "Snapshot belongs to a different project path."}
    old = {item["path"]: item["sha256"] for item in manifest.get("files", [])}
    current = {}
    for file_path in _iter_files(root):
        if file_path.stat().st_size <= MAX_FILE_SIZE:
            current[file_path.relative_to(root).as_posix()] = _hash(file_path)
    added = sorted(set(current) - set(old))
    deleted = sorted(set(old) - set(current))
    modified = sorted(p for p in set(old) & set(current) if old[p] != current[p])
    return {"snapshot_id": snapshot_id, "added": added, "modified": modified, "deleted": deleted}


def restore_snapshot(snapshot_id, path="."):
    folder, manifest = _load_snapshot(snapshot_id)
    root = _safe_path(path)
    if str(root.relative_to(WORKSPACE)) != manifest.get("project"):
        return {"error": "Snapshot belongs to a different project path."}
    restored = []
    for item in manifest.get("files", []):
        source = folder / "files" / item["path"]
        destination = root / item["path"]
        if not source.is_file():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        restored.append(item["path"])
    return {"status": "restored", "snapshot_id": snapshot_id, "restored_files": restored, "extra_current_files_kept": True}


def build_snapshot_tools(registry):
    registry.register("create_snapshot", "Create a safe backup before major project changes. Argument: path optional.", create_snapshot)
    registry.register("list_snapshots", "List backups for a project. Argument: path optional.", list_snapshots)
    registry.register("compare_snapshot", "Compare current project files with a backup. Arguments: snapshot_id, path optional.", compare_snapshot)
    registry.register("restore_snapshot", "Restore files from a backup; extra current files are never deleted. Arguments: snapshot_id, path optional.", restore_snapshot)
    return registry
