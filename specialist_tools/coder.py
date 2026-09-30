from __future__ import annotations

import ast
from typing import Any

from tool_system import RiskLevel, ToolMetadata
from specialist_tools.file_manager import FileManagerTool


class CoderTool:
    metadata = ToolMetadata(
        name="coder",
        description=(
            "Assist with coding tasks through controlled workspace file operations. "
            "It can inspect source, apply exact text replacements, write code, and validate Python syntax."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["inspect", "write", "replace", "validate_python"],
                },
                "path": {"type": "string"},
                "content": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["operation", "path"],
            "additionalProperties": False,
        },
        output_format="JSON object containing the coding operation result.",
        risk_level=RiskLevel.WRITE,
        permission="workspace",
        timeout_seconds=20.0,
    )

    def __init__(self, file_manager: FileManagerTool) -> None:
        self.files = file_manager

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        operation = arguments.get("operation")
        path = arguments.get("path")

        if operation == "inspect":
            result = self.files.execute({"operation": "read", "path": path})
            if "content" not in result:
                return result
            content = result["content"]
            return {
                "path": path,
                "language": self._language(path),
                "characters": len(content),
                "lines": len(content.splitlines()),
                "preview": content[:12000],
            }

        if operation == "write":
            return self.files.execute({
                "operation": "write",
                "path": path,
                "content": arguments.get("content", ""),
            })

        if operation == "replace":
            current = self.files.execute({"operation": "read", "path": path})
            if "content" not in current:
                return current
            old_text = arguments.get("old_text")
            new_text = arguments.get("new_text")
            if not isinstance(old_text, str) or not old_text:
                raise ValueError("old_text must be a non-empty string.")
            if not isinstance(new_text, str):
                raise ValueError("new_text must be a string.")
            if current["content"].count(old_text) != 1:
                raise ValueError("old_text must occur exactly once before replacement.")
            updated = current["content"].replace(old_text, new_text)
            return self.files.execute({
                "operation": "write",
                "path": path,
                "content": updated,
            })

        if operation == "validate_python":
            current = self.files.execute({"operation": "read", "path": path})
            if "content" not in current:
                return current
            if not str(path).lower().endswith(".py"):
                raise ValueError("validate_python requires a .py file.")

            try:
                ast.parse(current["content"], filename=str(path))
                syntax = {"valid": True}
            except SyntaxError as exc:
                syntax = {
                    "valid": False,
                    "line": exc.lineno,
                    "column": exc.offset,
                    "message": exc.msg,
                    "text": exc.text,
                }

            return {"path": path, "syntax": syntax}

        raise ValueError("Unsupported coder operation.")

    @staticmethod
    def _language(path: str) -> str:
        suffix = str(path).lower().rsplit(".", 1)[-1] if "." in str(path) else ""
        return {
            "py": "python",
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "json": "json",
            "html": "html",
            "css": "css",
        }.get(suffix, "text")
