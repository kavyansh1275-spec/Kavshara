from __future__ import annotations

import ast
import math
import operator
from typing import Any

from tool_system import RiskLevel, ToolMetadata


class CalculatorTool:
    metadata = ToolMetadata(
        name="calculator",
        description=(
            "Perform deterministic arithmetic and numeric calculations. "
            "Use this instead of relying on the language model for arithmetic."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression such as '17% of 45000' or 'sqrt(81)'.",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        output_format="JSON object containing the normalized expression and numeric result.",
        risk_level=RiskLevel.SAFE,
        timeout_seconds=5.0,
    )

    _binary_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    _unary_ops = {ast.UAdd: operator.pos, ast.USub: operator.neg}
    _functions = {
        "abs": abs,
        "ceil": math.ceil,
        "floor": math.floor,
        "sqrt": math.sqrt,
        "round": round,
    }

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        expression = arguments.get("expression")
        if not isinstance(expression, str) or not expression.strip():
            raise ValueError("expression must be a non-empty string.")

        normalized = self._normalize(expression)
        tree = ast.parse(normalized, mode="eval")
        result = self._evaluate(tree.body)

        if not isinstance(result, (int, float)) or isinstance(result, bool):
            raise ValueError("Expression did not produce a numeric result.")
        if not math.isfinite(float(result)):
            raise ValueError("Result is not finite.")

        return {
            "expression": expression,
            "normalized_expression": normalized,
            "result": result,
        }

    def _normalize(self, expression: str) -> str:
        text = expression.strip().lower().replace(",", "")
        text = text.replace("×", "*").replace("÷", "/").replace("^", "**")

        import re
        percent_of = re.fullmatch(
            r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*%\s*of\s*"
            r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*",
            text,
        )
        if percent_of:
            return f"({percent_of.group(1)} / 100) * ({percent_of.group(2)})"

        return re.sub(
            r"(?P<number>[+-]?(?:\d+(?:\.\d*)?|\.\d+))\s*%",
            r"(\g<number> / 100)",
            text,
        )

    def _evaluate(self, node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in self._binary_ops:
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Exponent is too large.")
            return self._binary_ops[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in self._unary_ops:
            return self._unary_ops[type(node.op)](self._evaluate(node.operand))

        if isinstance(node, ast.Name) and node.id == "pi":
            return math.pi

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            function = self._functions.get(node.func.id)
            if function is None or node.keywords:
                raise ValueError("Unsupported calculator function.")
            return function(*[self._evaluate(arg) for arg in node.args])

        raise ValueError("Unsupported expression.")
