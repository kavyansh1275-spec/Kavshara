from dataclasses import dataclass
from permissions import get_permissions

@dataclass(frozen=True)
class RiskPolicy:
    level: str
    requires_confirmation: bool

POLICIES = {
    "LOW": RiskPolicy("LOW", False),
    "MEDIUM": RiskPolicy("MEDIUM", False),
    "HIGH": RiskPolicy("HIGH", True),
    "BLOCKED": RiskPolicy("BLOCKED", True),
}

def require_desktop_access():
    if get_permissions().get("desktop_access") is not True:
        return {
            "success": False,
            "status": "permission_required",
            "permission": "desktop_access",
            "message": "Desktop access is not enabled. Use /access and grant access first.",
        }
    return None

def policy_for(level):
    return POLICIES.get(level, POLICIES["BLOCKED"])
