from __future__ import annotations

import os

from tool_system import RiskLevel, ToolExecutor, ToolRegistry
from specialist_tools.calculator import CalculatorTool
from specialist_tools.coder import CoderTool
from specialist_tools.file_manager import FileManagerTool
from specialist_tools.researcher import ResearcherTool
from specialist_tools.terminal import TerminalTool


def build_specialist_registry() -> tuple[ToolRegistry, ToolExecutor]:
    registry = ToolRegistry()
    files = FileManagerTool()

    registry.register(CalculatorTool())
    registry.register(files)
    registry.register(CoderTool(files))
    registry.register(ResearcherTool())
    registry.register(TerminalTool())

    allowed = {
        RiskLevel.SAFE,
        RiskLevel.READ,
        RiskLevel.WRITE,
    }

    if os.getenv("KAVSHARA_ALLOW_EXECUTE", "").strip().lower() in {"1", "true", "yes"}:
        allowed.add(RiskLevel.EXECUTE)

    if os.getenv("KAVSHARA_ALLOW_NETWORK_RESEARCH", "").strip().lower() in {"1", "true", "yes"}:
        allowed.add(RiskLevel.NETWORK)

    return registry, ToolExecutor(registry, allowed_risk_levels=allowed)
