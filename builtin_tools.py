from pathlib import Path

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
    return {
        "path": str(target.relative_to(WORKSPACE)),
        "content": text[:20000],
        "truncated": len(text) > 20000,
    }


def write_file(path, content):
    target = _safe_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {
        "path": str(target.relative_to(WORKSPACE)),
        "bytes": target.stat().st_size,
        "status": "written",
    }


def build_default_registry():
    from tools import ToolRegistry
    from coding_tools import build_coding_tools
    from project_tools import build_project_tools

    registry = ToolRegistry()
    registry.register(
        "list_files",
        "List files/directories inside the workspace. Argument: path optional.",
        list_files,
    )
    registry.register(
        "read_file",
        "Read a UTF-8 text file inside the workspace. Argument: path.",
        read_file,
    )
    registry.register(
        "write_file",
        "Create or replace a UTF-8 text file inside the workspace. Arguments: path, content.",
        write_file,
    )
    build_coding_tools(registry)
    build_project_tools(registry)
    return registry
