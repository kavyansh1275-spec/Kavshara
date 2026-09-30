"""Kavshara V2 specialist tool architecture."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import asdict, dataclass, field
from enum import Enum
import time
from typing import Any, Protocol


class RiskLevel(str, Enum):
    SAFE = "safe"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    NETWORK = "network"


@dataclass(frozen=True)
class ToolMetadata:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_format: str
    risk_level: RiskLevel = RiskLevel.SAFE
    permission: str = "none"
    timeout_seconds: float = 30.0
    enabled: bool = True


@dataclass
class ToolResult:
    tool: str
    status: str
    output: Any = None
    error: str | None = None
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class SpecialistTool(Protocol):
    metadata: ToolMetadata

    def execute(self, arguments: dict[str, Any]) -> Any:
        ...


class ToolRegistry:
    """Central registry for V2 specialist tools."""

    def __init__(self) -> None:
        self._tools: dict[str, SpecialistTool] = {}

    def register(self, tool: SpecialistTool) -> SpecialistTool:
        name = tool.metadata.name.strip()
        if not name:
            raise ValueError("Tool name cannot be empty.")
        if name in self._tools:
            raise ValueError(f"Tool already registered: {name}")
        self._tools[name] = tool
        return tool

    def get(self, name: str) -> SpecialistTool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def metadata(self) -> list[dict[str, Any]]:
        return [
            {
                **asdict(tool.metadata),
                "risk_level": tool.metadata.risk_level.value,
            }
            for tool in self._tools.values()
            if tool.metadata.enabled
        ]

    def describe_for_agent(self) -> str:
        import json
        return json.dumps(self.metadata(), ensure_ascii=False, indent=2)


class ToolExecutor:
    """Single execution boundary for validation, permissions and timeouts."""

    def __init__(
        self,
        registry: ToolRegistry,
        allowed_risk_levels: set[RiskLevel] | None = None,
    ) -> None:
        self.registry = registry
        self.allowed_risk_levels = allowed_risk_levels or {
            RiskLevel.SAFE,
            RiskLevel.READ,
            RiskLevel.WRITE,
        }

    def execute(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        tool = self.registry.get(name)

        if tool is None:
            return ToolResult(
                tool=name,
                status="error",
                error=f"Unknown tool: {name}",
                duration_ms=_elapsed_ms(started),
            ).to_dict()

        metadata = tool.metadata
        if not metadata.enabled:
            return ToolResult(
                tool=name,
                status="error",
                error=f"Tool is disabled: {name}",
                duration_ms=_elapsed_ms(started),
            ).to_dict()

        if metadata.risk_level not in self.allowed_risk_levels:
            return ToolResult(
                tool=name,
                status="permission_denied",
                error=(
                    f"Risk level '{metadata.risk_level.value}' is not currently "
                    "allowed by Kavshara's tool policy."
                ),
                duration_ms=_elapsed_ms(started),
                metadata={"risk_level": metadata.risk_level.value},
            ).to_dict()

        if arguments is None:
            arguments = {}
        if not isinstance(arguments, dict):
            return ToolResult(
                tool=name,
                status="error",
                error="Tool arguments must be a JSON object.",
                duration_ms=_elapsed_ms(started),
            ).to_dict()

        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(tool.execute, arguments)
                output = future.result(timeout=metadata.timeout_seconds)

            return ToolResult(
                tool=name,
                status="success",
                output=output,
                duration_ms=_elapsed_ms(started),
                metadata={"risk_level": metadata.risk_level.value},
            ).to_dict()
        except FutureTimeoutError:
            return ToolResult(
                tool=name,
                status="timeout",
                error=f"Tool exceeded {metadata.timeout_seconds:.1f}s timeout.",
                duration_ms=_elapsed_ms(started),
                metadata={"risk_level": metadata.risk_level.value},
            ).to_dict()
        except Exception as exc:
            return ToolResult(
                tool=name,
                status="error",
                error=f"{type(exc).__name__}: {exc}",
                duration_ms=_elapsed_ms(started),
                metadata={"risk_level": metadata.risk_level.value},
            ).to_dict()


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)
