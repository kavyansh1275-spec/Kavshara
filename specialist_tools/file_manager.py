from __future__ import annotations

from pathlib import Path
from typing import Any

from tool_system import RiskLevel, ToolMetadata

WORKSPACE = Path("workspace").resolve()
MAX_READ_BYTES = 1_000_000
MAX_LIST_ITEMS = 1000
IGNORED_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".venv", "venv",
    "node_modules", ".next", "dist", "build", ".idea", ".vscode",
    ".kavshara",
}


class FileManagerTool:
    metadata = ToolMetadata(
        name="file_manager",
        description=(
            "Inspect and modify files inside Kavshara's approved workspace. "
            "Supports listing, reading, writing and text search without access outside the workspace."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["list", "read", "write", "search"],
                },
                "path": {"type": "string", "description": "Workspace-relative path."},
                "content": {"type": "string", "description": "Content for write operations."},
                "query": {"type": "string", "description": "Text to search for."},
            },
            "required": ["operation"],
            "additionalProperties": False,
        },
        output_format="JSON object describing the requested filesystem operation.",
        risk_level=RiskLevel.WRITE,
        permission="workspace",
        timeout_seconds=15.0,
    )

    def __init__(self, workspace: Path | None = None) -> None:
        self.workspace = (workspace or WORKSPACE).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        operation = arguments.get("operation")
        if operation == "list":
            return self._list(arguments.get("path", "."))
        if operation == "read":
            return self._read(arguments.get("path"))
        if operation == "write":
            return self._write(arguments.get("path"), arguments.get("content"))
        if operation == "search":
            return self._search(arguments.get("query"), arguments.get("path", "."))
        raise ValueError("Unsupported file_manager operation.")

    def _safe_path(self, relative_path: str | None) -> Path:
        if not isinstance(relative_path, str) or not relative_path.strip():
            relative_path = "."
        candidate = (self.workspace / relative_path).resolve()
        if candidate != self.workspace and self.workspace not in candidate.parents:
            raise ValueError("Path must stay inside Kavshara's workspace.")
        return candidate

    def _list(self, path: str) -> dict[str, Any]:
        root = self._safe_path(path)
        if not root.is_dir():
            raise ValueError("Path is not a directory.")

        items = []
        for item in sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))[:MAX_LIST_ITEMS]:
            if item.name in IGNORED_DIRS:
                continue
            items.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "path": item.relative_to(self.workspace).as_posix(),
            })
        return {
            "operation": "list",
            "path": root.relative_to(self.workspace).as_posix(),
            "items": items,
        }

    def _read(self, path: str | None) -> dict[str, Any]:
        target = self._safe_path(path)
        if not target.is_file():
            raise ValueError("File does not exist.")
        if target.stat().st_size > MAX_READ_BYTES:
            raise ValueError("File is too large to read through File Manager.")
        return {
            "operation": "read",
            "path": target.relative_to(self.workspace).as_posix(),
            "content": target.read_text(encoding="utf-8", errors="replace"),
        }

    def _write(self, path: str | None, content: Any) -> dict[str, Any]:
        if not isinstance(path, str) or not path.strip():
            raise ValueError("path is required for write.")
        if not isinstance(content, str):
            raise ValueError("content must be a string.")

        target = self._safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {
            "operation": "write",
            "path": target.relative_to(self.workspace).as_posix(),
            "bytes": target.stat().st_size,
            "status": "written",
        }

    def _search(self, query: Any, path: str) -> dict[str, Any]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string.")

        root = self._safe_path(path)
        if not root.is_dir():
            raise ValueError("Search path is not a directory.")

        results = []
        needle = query.lower()

        for file_path in root.rglob("*"):
            if len(results) >= 100:
                break
            if not file_path.is_file() or any(part in IGNORED_DIRS for part in file_path.parts):
                continue
            try:
                if file_path.stat().st_size > MAX_READ_BYTES:
                    continue
                lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue

            matches = [
                {"line": number, "text": line[:500]}
                for number, line in enumerate(lines, 1)
                if needle in line.lower()
            ][:10]

            if matches:
                results.append({
                    "path": file_path.relative_to(self.workspace).as_posix(),
                    "matches": matches,
                })

        return {"operation": "search", "query": query, "results": results}
