from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from tool_system import RiskLevel, ToolMetadata

WORKSPACE = Path("workspace").resolve()
MAX_OUTPUT = 12000
DEFAULT_TIMEOUT = 10

ALLOWED_EXECUTABLES = {
    "python", "python3", "py", "pytest", "pip", "pip3",
    "node", "npm", "git", "ruff", "mypy",
}


class TerminalTool:
    metadata = ToolMetadata(
        name="terminal",
        description=(
            "Run approved development commands inside Kavshara's workspace. "
            "Uses argument arrays, no shell, an executable allowlist, output limits, and a timeout."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Executable plus arguments; shell syntax is not supported.",
                },
                "timeout_seconds": {"type": "number", "minimum": 1, "maximum": 30},
                "cwd": {"type": "string", "description": "Workspace-relative working directory."},
            },
            "required": ["command"],
            "additionalProperties": False,
        },
        output_format="JSON object containing return code, stdout, stderr, and execution status.",
        risk_level=RiskLevel.EXECUTE,
        permission="terminal",
        timeout_seconds=30.0,
    )

    def __init__(self, workspace: Path | None = None) -> None:
        self.workspace = (workspace or WORKSPACE).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        command = arguments.get("command")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(item, str) and item for item in command)
        ):
            raise ValueError("command must be a non-empty list of strings.")

        executable = Path(command[0]).name.lower()
        if executable not in ALLOWED_EXECUTABLES:
            raise PermissionError(
                f"Executable '{command[0]}' is not allowed by the controlled terminal policy."
            )

        cwd = self._safe_cwd(arguments.get("cwd", "."))
        timeout = float(arguments.get("timeout_seconds", DEFAULT_TIMEOUT))
        timeout = max(1.0, min(timeout, 30.0))

        env = os.environ.copy()
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            env=env,
        )
        return {
            "status": "success" if result.returncode == 0 else "failed",
            "return_code": result.returncode,
            "stdout": result.stdout[:MAX_OUTPUT],
            "stderr": result.stderr[:MAX_OUTPUT],
            "cwd": str(cwd.relative_to(self.workspace)),
            "command": command,
        }

    def _safe_cwd(self, relative: str) -> Path:
        if not isinstance(relative, str):
            raise ValueError("cwd must be a workspace-relative string.")

        candidate = (self.workspace / relative).resolve()
        if candidate != self.workspace and self.workspace not in candidate.parents:
            raise ValueError("Terminal cwd must stay inside Kavshara's workspace.")
        if not candidate.is_dir():
            raise ValueError("Terminal cwd is not a directory.")
        return candidate
