from __future__ import annotations
from typing import Any

class ValidationError(ValueError):
    pass

def validate_schema(arguments: dict[str, Any], schema: dict[str, Any]) -> None:
    if not isinstance(arguments, dict):
        raise ValidationError("Arguments must be an object.")
    props = schema.get("properties", {})
    for name in schema.get("required", []):
        if name not in arguments:
            raise ValidationError(f"Missing required argument: {name}")
    unknown = set(arguments) - set(props)
    if unknown:
        raise ValidationError(f"Unknown argument(s): {', '.join(sorted(unknown))}")
    for name, value in arguments.items():
        spec = props[name]
        kind = spec.get("type")
        if kind == "string" and not isinstance(value, str):
            raise ValidationError(f"{name} must be a string.")
        if kind == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
            raise ValidationError(f"{name} must be an integer.")
        if kind == "array" and not isinstance(value, list):
            raise ValidationError(f"{name} must be an array.")
        if kind == "string" and len(value) < spec.get("minLength", 0):
            raise ValidationError(f"{name} is too short.")
        if kind == "string" and len(value) > spec.get("maxLength", 10**9):
            raise ValidationError(f"{name} is too long.")
        if kind == "integer" and value < spec.get("minimum", -10**9):
            raise ValidationError(f"{name} is below the allowed minimum.")
        if kind == "integer" and value > spec.get("maximum", 10**9):
            raise ValidationError(f"{name} exceeds the allowed maximum.")
        if "enum" in spec and value not in spec["enum"]:
            raise ValidationError(f"{name} must be one of: {', '.join(map(str, spec['enum']))}")
        if kind == "array":
            item_spec = spec.get("items", {})
            if item_spec.get("type") == "string" and not all(isinstance(x, str) for x in value):
                raise ValidationError(f"Every item in {name} must be a string.")
