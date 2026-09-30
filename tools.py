from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]
    schema: dict = field(default_factory=lambda: {"type": "object", "properties": {}})
    risk_level: str = "LOW"
    requires_confirmation: bool = False
    timeout: int = 30

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name, description, function, schema=None, risk_level="LOW",
                 requires_confirmation=False, timeout=30):
        self._tools[name] = Tool(
            name=name,
            description=description,
            function=function,
            schema=schema or {"type": "object", "properties": {}},
            risk_level=risk_level,
            requires_confirmation=requires_confirmation,
            timeout=timeout,
        )

    def get(self, name):
        return self._tools.get(name)

    def names(self):
        return list(self._tools.keys())

    def descriptions(self):
        return [{
            "name": t.name,
            "description": t.description,
            "input_schema": t.schema,
            "risk_level": t.risk_level,
            "requires_confirmation": t.requires_confirmation,
            "timeout_seconds": t.timeout,
        } for t in self._tools.values()]

    def execute(self, name, arguments=None):
        tool = self.get(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        args = arguments or {}
        if not isinstance(args, dict):
            raise ValueError("Tool arguments must be an object.")
        return tool.function(**args)
