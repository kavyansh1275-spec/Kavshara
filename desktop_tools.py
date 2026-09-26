import os
from pathlib import Path

from permissions import get_permissions

HOME = Path.home().resolve()

# Read/open access is intentionally limited to ordinary user-content locations.
COMMON_ROOTS = [
    HOME / "Desktop",
    HOME / "Documents",
    HOME / "Downloads",
    HOME / "Pictures",
    HOME / "Videos",
    HOME / "Music",
    HOME / "OneDrive",
]


def _require_access():
    if not get_permissions().get("desktop_access"):
        return {"error": "Desktop access is not granted. Use the startup permission prompt first."}
    return None


def _roots():
    return [root for root in COMMON_ROOTS if root.exists()]


def _is_allowed(target):
    target = target.resolve()
    return any(target == root or root in target.parents for root in _roots())


def list_desktop_roots():
    denied = _require_access()
    if denied:
        return denied
    return {"roots": [str(root) for root in _roots()]}


def search_desktop(query, max_results=50):
    denied = _require_access()
    if denied:
        return denied

    query = str(query).strip().lower()
    if not query:
        return {"error": "query is required."}

    results = []
    ignored = {".git", "node_modules", "__pycache__", ".venv", "venv", ".kavshara"}

    for root in _roots():
        for current, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if d not in ignored]
            for name in files + dirs:
                if query in name.lower():
                    results.append(str(Path(current) / name))
                    if len(results) >= int(max_results):
                        return {"query": query, "results": results}
    return {"query": query, "results": results}


def list_directory(path):
    denied = _require_access()
    if denied:
        return denied

    target = Path(path).expanduser().resolve()
    if not _is_allowed(target):
        return {"error": "For safety, directory access is limited to approved user-content folders."}
    if not target.exists() or not target.is_dir():
        return {"error": "Directory does not exist."}

    try:
        entries = []
        for item in sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))[:200]:
            entries.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "path": str(item),
            })
        return {"path": str(target), "entries": entries}
    except OSError as exc:
        return {"error": str(exc)}


def read_desktop_file(path, max_chars=30000):
    denied = _require_access()
    if denied:
        return denied

    target = Path(path).expanduser().resolve()
    if not _is_allowed(target):
        return {"error": "For safety, file access is limited to approved user-content folders."}
    if not target.exists() or not target.is_file():
        return {"error": "File does not exist."}
    if target.stat().st_size > 2_000_000:
        return {"error": "File is too large for text inspection."}

    try:
        return {
            "path": str(target),
            "content": target.read_text(encoding="utf-8")[:max_chars],
            "truncated": target.stat().st_size > max_chars,
        }
    except UnicodeDecodeError:
        return {"error": "File is not a UTF-8 text file."}
    except OSError as exc:
        return {"error": str(exc)}


def open_path(path):
    denied = _require_access()
    if denied:
        return denied

    target = Path(path).expanduser().resolve()
    if not _is_allowed(target):
        return {"error": "For safety, only approved user-content paths can be opened."}
    if not target.exists():
        return {"error": "Path does not exist."}

    try:
        os.startfile(str(target))
        return {"status": "opened", "path": str(target)}
    except OSError as exc:
        return {"status": "failed", "error": str(exc)}


def get_file_info(path):
    denied = _require_access()
    if denied:
        return denied

    target = Path(path).expanduser().resolve()
    if not _is_allowed(target):
        return {"error": "For safety, file access is limited to approved user-content folders."}
    if not target.exists():
        return {"error": "Path does not exist."}

    try:
        stat = target.stat()
        return {
            "path": str(target),
            "name": target.name,
            "type": "directory" if target.is_dir() else "file",
            "size_bytes": stat.st_size if target.is_file() else None,
            "extension": target.suffix if target.is_file() else "",
        }
    except OSError as exc:
        return {"error": str(exc)}


def open_url(url):
    denied = _require_access()
    if denied:
        return denied
    url = str(url).strip()
    if not (url.startswith('https://') or url.startswith('http://')):
        return {'error': 'Only http:// and https:// URLs are allowed.'}
    try:
        os.startfile(url)
        return {'status': 'opened', 'url': url}
    except OSError as exc:
        return {'status': 'failed', 'error': str(exc)}


def _allowed_target(path):
    target = Path(path).expanduser().resolve()
    if not _is_allowed(target):
        return None, {"error": "For safety, file access is limited to approved user-content folders."}
    return target, None


def write_desktop_file(path, content):
    denied = _require_access()
    if denied:
        return denied
    target, error = _allowed_target(path)
    if error:
        return error
    if target.exists() and target.is_dir():
        return {"error": "Target is a directory."}
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content), encoding="utf-8")
        return {"status": "written", "path": str(target), "size_bytes": target.stat().st_size}
    except OSError as exc:
        return {"status": "failed", "error": str(exc)}


def create_directory(path):
    denied = _require_access()
    if denied:
        return denied
    target, error = _allowed_target(path)
    if error:
        return error
    try:
        target.mkdir(parents=True, exist_ok=True)
        return {"status": "created", "path": str(target)}
    except OSError as exc:
        return {"status": "failed", "error": str(exc)}


def copy_desktop_file(source, destination):
    denied = _require_access()
    if denied:
        return denied
    src, error = _allowed_target(source)
    if error:
        return error
    dst, error = _allowed_target(destination)
    if error:
        return error
    if not src.exists() or not src.is_file():
        return {"error": "Source file does not exist or is not a file."}
    try:
        import shutil
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return {"status": "copied", "source": str(src), "destination": str(dst)}
    except OSError as exc:
        return {"status": "failed", "error": str(exc)}


def rename_desktop_path(source, destination):
    denied = _require_access()
    if denied:
        return denied
    src, error = _allowed_target(source)
    if error:
        return error
    dst, error = _allowed_target(destination)
    if error:
        return error
    if not src.exists():
        return {"error": "Source path does not exist."}
    if dst.exists():
        return {"error": "Destination already exists; rename was not performed."}
    try:
        src.rename(dst)
        return {"status": "renamed", "source": str(src), "destination": str(dst)}
    except OSError as exc:
        return {"status": "failed", "error": str(exc)}


def build_desktop_tools(registry):
    registry.register(
        "list_desktop_roots",
        "List approved user-content folders available after desktop permission is granted.",
        list_desktop_roots,
    )
    registry.register(
        "search_desktop",
        "Search filenames in approved user-content folders. Arguments: query; max_results optional.",
        search_desktop,
    )
    registry.register(
        "list_directory",
        "List entries in an approved user-content directory. Argument: path.",
        list_directory,
    )
    registry.register(
        "read_desktop_file",
        "Read a UTF-8 text file from an approved user-content folder. Argument: path.",
        read_desktop_file,
    )
    registry.register(
        "open_path",
        "Open an approved file or folder with the Windows default application. Argument: path.",
        open_path,
    )
    registry.register(
        "get_file_info",
        "Get basic metadata for an approved file or folder. Argument: path.",
        get_file_info,
    )
    registry.register("system_info", "Return basic Windows and Kavshara runtime information.", system_info)
    registry.register("open_url", "Open an http or https URL in the default browser. Argument: url.", open_url)
    registry.register("write_desktop_file", "Write UTF-8 text to an approved user-content file. Arguments: path, content.", write_desktop_file)
    registry.register("create_directory", "Create a directory inside approved user-content folders. Argument: path.", create_directory)
    registry.register("copy_desktop_file", "Copy an approved file to another approved location. Arguments: source, destination.", copy_desktop_file)
    registry.register("rename_desktop_path", "Rename an approved file or folder without overwriting an existing destination. Arguments: source, destination.", rename_desktop_path)
    return registry


def system_info():
    denied = _require_access()
    if denied:
        return denied
    import platform
    return {'os': platform.platform(), 'windows_version': platform.version(), 'machine': platform.machine(), 'python': platform.python_version(), 'user': os.environ.get('USERNAME', ''), 'home': str(HOME)}
