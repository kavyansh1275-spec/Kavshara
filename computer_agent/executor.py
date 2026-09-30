from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None
try:
    import pyautogui
except Exception:
    # Headless CI/Linux environments may not have a display. Windows runtime still uses pyautogui.
    pyautogui = None

START_MENU_DIRS = [
    Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft/Windows/Start Menu/Programs",
]

def _norm(value):
    return " ".join(value.lower().replace(".lnk", "").replace(".exe", "").split())

def resolve_application(name):
    target = _norm(name)
    if not target:
        return None
    direct = shutil.which(name)
    if direct:
        return direct
    for root in START_MENU_DIRS:
        if not root.exists():
            continue
        try:
            for path in root.rglob("*.lnk"):
                if _norm(path.stem) == target:
                    return path
        except OSError:
            pass
    common = {
        "vs code": "Code.exe",
        "visual studio code": "Code.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
    }
    return shutil.which(common[target]) if target in common else None

def launch_application(application):
    resolved = resolve_application(application)
    if not resolved:
        return {"success": False, "error_type": "ApplicationNotFound", "message": f"Could not resolve: {application}"}
    try:
        os.startfile(str(resolved))
        return {"success": True, "resolved_target": str(resolved)}
    except (OSError, AttributeError) as exc:
        return {"success": False, "error_type": type(exc).__name__, "message": str(exc)}

def close_application(application):
    if psutil is None:
        return {"success": False, "error_type": "DependencyMissing", "message": "psutil is required."}
    target = _norm(application)
    matches = []
    for process in psutil.process_iter(["pid", "name"]):
        try:
            name = _norm(process.info.get("name") or "")
            if target == name or target == _norm(Path(name).stem):
                matches.append(process)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not matches:
        return {"success": False, "error_type": "ProcessNotFound", "message": f"No process matched: {application}"}
    for process in matches[:5]:
        try:
            process.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    gone, alive = psutil.wait_procs(matches[:5], timeout=3)
    return {"success": bool(gone), "closed_pids": [p.pid for p in gone], "still_running": [p.pid for p in alive]}

def open_path(path):
    target = Path(path).expanduser().resolve()
    if not target.exists():
        return {"success": False, "error_type": "PathNotFound", "message": str(target)}
    try:
        os.startfile(str(target))
        return {"success": True, "path": str(target)}
    except (OSError, AttributeError) as exc:
        return {"success": False, "error_type": type(exc).__name__, "message": str(exc)}

def take_screenshot(path):
    if pyautogui is None:
        return {"success": False, "error_type": "DependencyMissing", "message": "pyautogui is required."}
    try:
        target = Path(path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        image = pyautogui.screenshot()
        image.save(target)
        return {"success": True, "path": str(target), "size": {"width": image.width, "height": image.height}}
    except Exception as exc:
        return {"success": False, "error_type": type(exc).__name__, "message": str(exc)}

def screen_size():
    if pyautogui is None:
        return None
    try:
        size = pyautogui.size()
        return int(size.width), int(size.height)
    except Exception:
        return None

def mouse(action, x, y, button="left"):
    if pyautogui is None:
        return {"success": False, "error_type": "DependencyMissing", "message": "pyautogui is required."}
    size = screen_size()
    if not size or not (0 <= x < size[0] and 0 <= y < size[1]):
        return {"success": False, "error_type": "InvalidCoordinates", "message": "Coordinates are outside the primary display."}
    try:
        if action == "move":
            pyautogui.moveTo(x, y, duration=0.1)
        elif action == "click":
            pyautogui.click(x, y, button=button)
        elif action == "double_click":
            pyautogui.doubleClick(x, y, button=button)
        elif action == "right_click":
            pyautogui.rightClick(x, y)
        else:
            return {"success": False, "error_type": "InvalidMouseAction", "message": action}
        return {"success": True, "action": action, "x": x, "y": y, "button": button}
    except Exception as exc:
        return {"success": False, "error_type": type(exc).__name__, "message": str(exc)}

ALLOWED_KEYS = {
    "enter","esc","escape","tab","space","backspace","delete","home","end","left","right","up","down",
    "shift","ctrl","alt","win","command","insert","pageup","pagedown","capslock","numlock","scrolllock",
    "f1","f2","f3","f4","f5","f6","f7","f8","f9","f10","f11","f12"
}

def keyboard(action, text=None, key=None, keys=None):
    if pyautogui is None:
        return {"success": False, "error_type": "DependencyMissing", "message": "pyautogui is required."}
    try:
        if action == "type":
            if len(text or "") > 5000:
                return {"success": False, "error_type": "InputTooLong", "message": "Typed text exceeds 5000 characters."}
            pyautogui.write(text or "", interval=0.01)
        elif action == "press":
            normalized = (key or "").lower()
            if normalized not in ALLOWED_KEYS and not (len(normalized) == 1 and normalized.isprintable()):
                return {"success": False, "error_type": "InvalidKey", "message": normalized}
            pyautogui.press(normalized)
        elif action == "hotkey":
            normalized = [(k or "").lower() for k in (keys or [])]
            if not normalized or len(normalized) > 5 or any(k not in ALLOWED_KEYS and len(k) != 1 for k in normalized):
                return {"success": False, "error_type": "InvalidHotkey", "message": normalized}
            pyautogui.hotkey(*normalized)
        else:
            return {"success": False, "error_type": "InvalidKeyboardAction", "message": action}
        return {"success": True, "action": action}
    except Exception as exc:
        return {"success": False, "error_type": type(exc).__name__, "message": str(exc)}

SAFE_COMMANDS = {
    "dir": None, "where": None, "whoami": None, "echo": None, "ver": None, "hostname": None,
    "python": {"--version", "-V"}, "py": {"--version", "-V"},
    "pip": {"--version", "-V"},
    "git": {"--version", "version", "status", "branch", "log", "diff"},
}
FORBIDDEN_SHELL_CHARS = set("&|><;$" + chr(96) + "\\n\\r")

def terminal(command, cwd=None, timeout=10):
    if not isinstance(command, str) or not command.strip():
        return {"success": False, "error_type": "InvalidCommand", "message": "command must be non-empty."}
    if any(char in command for char in FORBIDDEN_SHELL_CHARS):
        return {"success": False, "error_type": "BlockedCommand", "message": "Shell operators are not allowed."}
    parts = command.strip().split()
    executable = parts[0].lower()
    if executable not in SAFE_COMMANDS:
        return {"success": False, "error_type": "BlockedCommand", "message": f"Not allowlisted: {executable}"}
    allowed = SAFE_COMMANDS[executable]
    if allowed is not None and (len(parts) < 2 or parts[1].lower() not in allowed):
        return {"success": False, "error_type": "BlockedCommand", "message": f"Arguments not allowlisted for: {executable}"}
    working = Path(cwd).expanduser().resolve() if cwd else Path.cwd()
    if not working.is_dir():
        return {"success": False, "error_type": "InvalidWorkingDirectory", "message": str(working)}
    timeout = max(1, min(int(timeout), 30))
    try:
        result = subprocess.run(parts, cwd=working, capture_output=True, text=True, timeout=timeout, shell=False)
        return {"success": result.returncode == 0, "return_code": result.returncode,
                "stdout": result.stdout[:12000], "stderr": result.stderr[:12000], "timeout": timeout}
    except subprocess.TimeoutExpired:
        return {"success": False, "error_type": "Timeout", "message": f"Exceeded {timeout} seconds."}
    except OSError as exc:
        return {"success": False, "error_type": type(exc).__name__, "message": str(exc)}
