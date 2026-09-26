import os
from pathlib import Path

from permissions import get_permissions

HOME = Path.home().resolve()
COMMON_ROOTS = [
    HOME / "Desktop",
    HOME / "Documents",
    HOME / "Downloads",
]


def _require_access():
    if not get_permissions().get("desktop_access"):
        return {"error": "Desktop access is not granted. Use the startup permission prompt first."}
    return None


def list_desktop_roots():
    denied = _require_access()
    if denied:
        return denied
    roots = []
    for root in COMMON_ROOTS:
        if root.exists():
            roots.append(str(root))
    return {"roots": roots}


def search_desktop(query, max_results=50):
    denied = _require_access()
    if denied:
        return denied
    query = str(query).strip().lower()
    if not query:
        return {"error": "query is required."}

    results = []
    for root in COMMON_ROOTS:
        if not root.exists():
            continue
        for current, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".venv", "venv"}]
            for name in files + dirs:
                if query in name.lower():
                    results.append(str(Path(current) / name))
                    if len(results) >= int(max_results):
                        return {"query": query, "results": results}
    return {"query": query, "results": results}


def read_desktop_file(path, max_chars=30000):
    denied = _require_access()
    if denied:
        return denied
    target = Path(path).expanduser().resolve()
    allowed = any(target == root or root in target.parents for root in COMMON_ROOTS if root.exists())
    if not allowed:
        return {"error": "For safety, file access is limited to Desktop, Documents, and Downloads."}
    if not target.exists() or not target.is_file():
        return {"error": "File does not exist."}
    if target.stat().st_size > 2_000_000:
        return {"error": "File is too large for text inspection."}
    try:
        return {"path": str(target), "content": target.read_text(encoding="utf-8")[:max_chars]}
    except UnicodeDecodeError:
        return {"error": "File is not a UTF-8 text file."}
    except OSError as exc:
        return {"error": str(exc)}


def build_desktop_tools(registry):
    registry.register(
        "list_desktop_roots",
        "List accessible common Windows user folders after desktop permission is granted.",
        list_desktop_roots,
    )
    registry.register(
        "search_desktop",
        "Search filenames in Desktop, Documents, and Downloads. Arguments: query; max_results optional.",
        search_desktop,
    )
    registry.register(
        "read_desktop_file",
        "Read a UTF-8 text file from Desktop, Documents, or Downloads. Argument: path.",
        read_desktop_file,
    )
    return registry
