from pathlib import Path
import subprocess
import sys

WORKSPACE = Path("workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)

MAX_OUTPUT = 12000
TIMEOUT_SECONDS = 10


def _safe_path(relative_path):
    candidate = (WORKSPACE / relative_path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Path must stay inside Kavshara's workspace.")
    return candidate


def run_python(path, args=None):
    target = _safe_path(path)
    if not target.exists() or not target.is_file():
        return {"error": "Python file does not exist."}
    if target.suffix.lower() != ".py":
        return {"error": "run_python only accepts .py files."}

    command = [sys.executable, str(target)]
    if args:
        if not isinstance(args, list) or not all(isinstance(x, str) for x in args):
            return {"error": "args must be a list of strings."}
        command.extend(args[:10])

    try:
        result = subprocess.run(
            command,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "return_code": result.returncode,
            "stdout": result.stdout[:MAX_OUTPUT],
            "stderr": result.stderr[:MAX_OUTPUT],
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "error": f"Execution exceeded {TIMEOUT_SECONDS} seconds."}
    except OSError as exc:
        return {"status": "error", "error": str(exc)}


def inspect_python(path):
    target = _safe_path(path)
    if not target.exists() or not target.is_file():
        return {"error": "Python file does not exist."}
    if target.suffix.lower() != ".py":
        return {"error": "inspect_python only accepts .py files."}

    source = target.read_text(encoding="utf-8")
    try:
        compile(source, str(target), "exec")
        syntax = {"valid": True}
    except SyntaxError as exc:
        syntax = {
            "valid": False,
            "line": exc.lineno,
            "offset": exc.offset,
            "message": exc.msg,
            "text": exc.text,
        }

    return {
        "path": str(target.relative_to(WORKSPACE)),
        "characters": len(source),
        "lines": len(source.splitlines()),
        "syntax": syntax,
    }


def build_coding_tools(registry):
    registry.register(
        "inspect_python",
        "Check a Python file for syntax errors. Argument: path.",
        inspect_python,
    )
    registry.register(
        "run_python",
        "Run a Python file inside the workspace with a short timeout. Arguments: path, args optional list of strings.",
        run_python,
    )
    return registry
