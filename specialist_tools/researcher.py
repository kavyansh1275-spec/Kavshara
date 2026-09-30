from __future__ import annotations

from typing import Any, Callable

from tool_system import RiskLevel, ToolMetadata


class ResearcherTool:
    """Provider-neutral research interface; a search backend can be injected later."""

    metadata = ToolMetadata(
        name="researcher",
        description=(
            "Research a topic through a provider-neutral search interface. "
            "It can later be connected to web-search without changing the agent protocol."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Research question or topic."},
                "max_sources": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        output_format="JSON object containing query, sources, and provider status.",
        risk_level=RiskLevel.NETWORK,
        permission="network_research",
        timeout_seconds=30.0,
    )

    def __init__(self, provider: Callable[..., dict[str, Any]] | None = None) -> None:
        self.provider = provider

    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string.")

        max_sources = int(arguments.get("max_sources", 5))
        max_sources = max(1, min(max_sources, 20))

        if self.provider is None:
            return {
                "status": "provider_not_configured",
                "query": query.strip(),
                "max_sources": max_sources,
                "sources": [],
                "message": "Research interface is ready; connect a web-search provider in a later version.",
            }

        return self.provider(query.strip(), max_sources=max_sources)
