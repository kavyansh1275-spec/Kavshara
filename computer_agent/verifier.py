import time
from pathlib import Path
from .executor import resolve_application, screen_size

try:
    import psutil
except ImportError:
    psutil = None

def verify_open_application(name):
    time.sleep(0.7)
    resolved = resolve_application(name)
    if psutil is None:
        return {"verified": bool(resolved), "method": "target_resolution"}
    target = Path(str(resolved)).stem.lower() if resolved else name.lower().replace(" ", "")
    pids = []
    for process in psutil.process_iter(["pid", "name"]):
        try:
            process_name = Path(process.info.get("name") or "").stem.lower()
            if target and (target == process_name or target in process_name):
                pids.append(process.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {"verified": bool(pids), "method": "process_check", "pids": pids[:10]}

def verify_path(path):
    return {"verified": Path(path).expanduser().exists(), "method": "path_exists"}

def verify_screen():
    size = screen_size()
    return {"verified": bool(size), "method": "screen_size", "size": size}
