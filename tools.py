from dataclasses import dataclass
from typing import Callable


@dataclass
class Tool:
    name: str
    description: str
    function: Callable


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, function: Callable):
        self._tools[name] = Tool(name, description, function)

    def get(self, name: str):
        return self._tools.get(name)

    def descriptions(self):
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self._tools.values()
        ]

    def names(self):
        return list(self._tools.keys())
