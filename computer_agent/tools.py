from datetime import datetime
from pathlib import Path
from tools import ToolRegistry
from .executor import close_application, keyboard, launch_application, mouse, open_path, take_screenshot, terminal
from .logging import log_action
from .safety import policy_for, require_desktop_access
from .schemas import ValidationError, validate_schema
from .verifier import verify_open_application, verify_path, verify_screen

SCREENSHOT_DIR = Path("data/computer_screenshots")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

EMPTY_SCHEMA = {"type": "object", "properties": {}}
APP_SCHEMA = {"type": "object", "required": ["application"], "properties": {"application": {"type": "string", "minLength": 1, "maxLength": 200}}}
PATH_SCHEMA = {"type": "object", "required": ["path"], "properties": {"path": {"type": "string", "minLength": 1, "maxLength": 1000}}}
MOUSE_SCHEMA = {"type": "object", "required": ["x", "y"], "properties": {
    "x": {"type": "integer", "minimum": 0, "maximum": 10000},
    "y": {"type": "integer", "minimum": 0, "maximum": 10000},
    "button": {"type": "string", "enum": ["left", "right", "middle"]},
}}
TYPE_SCHEMA = {"type": "object", "required": ["text"], "properties": {"text": {"type": "string", "maxLength": 5000}}}
PRESS_SCHEMA = {"type": "object", "required": ["key"], "properties": {"key": {"type": "string", "minLength": 1, "maxLength": 30}}}
HOTKEY_SCHEMA = {"type": "object", "required": ["keys"], "properties": {"keys": {"type": "array", "items": {"type": "string"}}}}
TERMINAL_SCHEMA = {"type": "object", "required": ["command"], "properties": {
    "command": {"type": "string", "minLength": 1, "maxLength": 300},
    "cwd": {"type": "string", "maxLength": 1000},
    "timeout": {"type": "integer", "minimum": 1, "maximum": 30},
}}

def _run(tool_name, action, args, schema, risk, function, verifier=None):
    started = datetime.utcnow().isoformat() + "Z"
    try:
        validate_schema(args, schema)
    except ValidationError as exc:
        result = {"success": False, "status": "validation_error", "error_type": "ValidationError", "message": str(exc)}
        log_action(action, tool_name, args, risk, False, started, datetime.utcnow().isoformat()+"Z", False, False, "ValidationError")
        return result
    permission_error = require_desktop_access()
    if permission_error:
        log_action(action, tool_name, args, risk, False, started, datetime.utcnow().isoformat()+"Z", False, False, "PermissionRequired")
        return permission_error
    policy = policy_for(risk)
    if policy.level == "BLOCKED":
        log_action(action, tool_name, args, risk, False, started, datetime.utcnow().isoformat()+"Z", False, False, "BlockedAction")
        return {"success": False, "status": "blocked", "error_type": "BlockedAction"}
    if policy.requires_confirmation:
        log_action(action, tool_name, args, risk, False, started, datetime.utcnow().isoformat()+"Z", False, False, "ConfirmationRequired")
        return {"success": False, "status": "confirmation_required", "risk_level": risk,
                "message": "This action requires explicit user confirmation."}
    try:
        raw = function(**args)
        success = bool(raw.get("success"))
        verification = verifier() if success and verifier else None
        verified = bool(verification and verification.get("verified"))
        result = {**raw, "action": action, "risk_level": risk, "verified": verified}
        if verification is not None:
            result["verification"] = verification
        log_action(action, tool_name, args, risk, False, started, datetime.utcnow().isoformat()+"Z",
                   success, verified, None if success else raw.get("error_type"))
        return result
    except Exception as exc:
        log_action(action, tool_name, args, risk, False, started, datetime.utcnow().isoformat()+"Z", False, False, type(exc).__name__)
        return {"success": False, "action": action, "error_type": type(exc).__name__, "message": str(exc), "verified": False}

def open_application(application):
    return _run("computer.open_application", "open_application", {"application": application}, APP_SCHEMA, "LOW",
                lambda application: launch_application(application), lambda: verify_open_application(application))

def close_app(application):
    return _run("computer.close_application", "close_application", {"application": application}, APP_SCHEMA, "MEDIUM",
                lambda application: close_application(application))

def open_file(path):
    target = Path(path).expanduser().resolve()
    return _run("computer.open_file", "open_file", {"path": path}, PATH_SCHEMA, "MEDIUM",
                lambda path: open_path(path), lambda: verify_path(str(target)))

def open_folder(path):
    target = Path(path).expanduser().resolve()
    return _run("computer.open_folder", "open_folder", {"path": path}, PATH_SCHEMA, "LOW",
                lambda path: open_path(path), lambda: verify_path(str(target)))

def take_screen():
    path = SCREENSHOT_DIR / f"screen_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
    return _run("computer.take_screenshot", "take_screenshot", {}, EMPTY_SCHEMA, "LOW",
                lambda: take_screenshot(str(path)), verify_screen)

def read_screen():
    result = take_screen()
    result["action"] = "read_screen"
    result["screen_information"] = {
        "screenshot_path": result.get("path"),
        "mode": "snapshot_only",
        "continuous_observation": False,
    }
    return result

def mouse_move(x, y):
    return _run("computer.mouse.move", "mouse_move", {"x": x, "y": y}, MOUSE_SCHEMA, "MEDIUM", lambda x, y: mouse("move", x, y))

def mouse_click(x, y, button="left"):
    return _run("computer.mouse.click", "mouse_click", {"x": x, "y": y, "button": button}, MOUSE_SCHEMA, "MEDIUM", lambda x, y, button: mouse("click", x, y, button))

def mouse_double_click(x, y, button="left"):
    return _run("computer.mouse.double_click", "mouse_double_click", {"x": x, "y": y, "button": button}, MOUSE_SCHEMA, "MEDIUM", lambda x, y, button: mouse("double_click", x, y, button))

def mouse_right_click(x, y):
    return _run("computer.mouse.right_click", "mouse_right_click", {"x": x, "y": y}, MOUSE_SCHEMA, "MEDIUM", lambda x, y: mouse("right_click", x, y))

def keyboard_type(text):
    return _run("computer.keyboard.type", "keyboard_type", {"text": text}, TYPE_SCHEMA, "MEDIUM", lambda text: keyboard("type", text=text))

def keyboard_press(key):
    return _run("computer.keyboard.press", "keyboard_press", {"key": key}, PRESS_SCHEMA, "MEDIUM", lambda key: keyboard("press", key=key))

def keyboard_hotkey(keys):
    return _run("computer.keyboard.hotkey", "keyboard_hotkey", {"keys": keys}, HOTKEY_SCHEMA, "MEDIUM", lambda keys: keyboard("hotkey", keys=keys))

def terminal_execute(command, cwd=None, timeout=10):
    return _run("computer.terminal.execute", "terminal_execute",
                {"command": command, "cwd": cwd, "timeout": timeout}, TERMINAL_SCHEMA, "HIGH",
                lambda command, cwd, timeout: terminal(command, cwd, timeout))
