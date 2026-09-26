from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, function: Callable[..., Any]):
        self._tools[name] = Tool(name, description, function)

    def get(self, name: str):
        return self._tools.get(name)

    def names(self):
        return list(self._tools.keys())

    def descriptions(self):
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def execute(self, name: str, arguments: dict | None = None):
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        return tool.function(**(arguments or {}))
