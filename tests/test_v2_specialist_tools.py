from pathlib import Path

from specialist_tools.calculator import CalculatorTool
from specialist_tools.file_manager import FileManagerTool
from specialist_tools.registry import build_specialist_registry
from tool_system import RiskLevel, ToolExecutor, ToolRegistry


def test_calculator_is_deterministic():
    result = CalculatorTool().execute({"expression": "17% of 45000"})
    assert result["result"] == 7650


def test_calculator_rejects_code():
    try:
        CalculatorTool().execute({"expression": "__import__('os').system('echo bad')"})
    except ValueError:
        return
    raise AssertionError("Unsafe calculator expression was accepted")


def test_registry_contains_initial_specialists():
    registry, _ = build_specialist_registry()
    assert registry.names() == [
        "calculator",
        "file_manager",
        "coder",
        "researcher",
        "terminal",
    ]


def test_file_manager_stays_inside_workspace(tmp_path: Path):
    files = FileManagerTool(tmp_path)
    files.execute({"operation": "write", "path": "hello.txt", "content": "hi"})
    result = files.execute({"operation": "read", "path": "hello.txt"})
    assert result["content"] == "hi"

    try:
        files.execute({"operation": "read", "path": "../outside.txt"})
    except ValueError:
        return
    raise AssertionError("Path traversal was accepted")


def test_execute_permission_is_disabled_by_default():
    registry, executor = build_specialist_registry()
    result = executor.execute("terminal", {"command": ["python", "--version"]})
    assert result["status"] == "permission_denied"
    assert RiskLevel.EXECUTE not in executor.allowed_risk_levels
