import os
from pathlib import Path

from permissions import get_permissions

START_MENU_DIRS = [
    Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
]


def _require_access():
    if not get_permissions().get("desktop_access"):
        return {"error": "Desktop access is not granted."}
    return None


def list_applications(query="", max_results=50):
    denied = _require_access()
    if denied:
        return denied

    query = str(query).strip().lower()
    results = []
    seen = set()

    for root in START_MENU_DIRS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix.lower() != ".lnk":
                continue
            name = path.stem
            if query and query not in name.lower():
                continue
            key = str(path.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            results.append({"name": name, "shortcut": str(path)})
            if len(results) >= int(max_results):
                return {"query": query, "applications": results}

    return {"query": query, "applications": results}


def launch_application(shortcut):
    denied = _require_access()
    if denied:
        return denied

    target = Path(shortcut).expanduser().resolve()
    allowed = any(root.exists() and (target == root or root in target.parents) for root in START_MENU_DIRS)
    if not allowed or target.suffix.lower() != ".lnk":
        return {"error": "For safety, only discovered Start Menu shortcuts can be launched."}

    try:
        os.startfile(str(target))
        return {"status": "launched", "shortcut": str(target)}
    except OSError as exc:
        return {"status": "failed", "error": str(exc)}


def build_app_tools(registry):
    registry.register(
        "list_applications",
        "Discover installed Windows Start Menu applications. Argument: query optional; max_results optional.",
        list_applications,
    )
    registry.register(
        "launch_application",
        "Launch a discovered Windows Start Menu shortcut. Argument: shortcut.",
        launch_application,
    )
    return registry
