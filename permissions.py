import json
from pathlib import Path

PERMISSION_FILE = Path("data/desktop_permissions.json")


def _load():
    if not PERMISSION_FILE.exists():
        return {}
    try:
        data = json.loads(PERMISSION_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save(data):
    PERMISSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    PERMISSION_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_permissions():
    return _load()


def request_desktop_access():
    permissions = _load()
    if permissions.get("desktop_access") is True:
        return {"status": "granted", "permissions": permissions}

    print("
Kavshara desktop access")
    print("This allows Kavshara to inspect files and discover installed applications.")
    print("It does NOT automatically grant unrestricted destructive actions or hidden access.")
    answer = input("Allow desktop access? [y/N]: ").strip().lower()

    granted = answer in {"y", "yes"}
    permissions["desktop_access"] = granted
    _save(permissions)

    return {
        "status": "granted" if granted else "denied",
        "permissions": permissions,
    }


def revoke_desktop_access():
    permissions = _load()
    permissions["desktop_access"] = False
    _save(permissions)
    return {"status": "revoked", "permissions": permissions}


def build_permission_tools(registry):
    registry.register(
        "get_desktop_permissions",
        "Check whether Kavshara has desktop access.",
        get_permissions,
    )
    registry.register(
        "revoke_desktop_access",
        "Revoke Kavshara desktop access.",
        revoke_desktop_access,
    )
    return registry
