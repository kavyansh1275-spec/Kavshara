import re
from urllib.parse import urlparse

from web_tools import web_search, fetch_url


def deep_research(query, max_sources=5):
    if not isinstance(query, str) or not query.strip():
        return {"error": "query must be a non-empty string."}

    search = web_search(query, max_sources)
    if search.get("error"):
        return search

    sources = []
    for result in search.get("results", [])[:max_sources]:
        url = result.get("url")
        if not url:
            continue
        fetched = fetch_url(url)
        text = fetched.get("content", "")
        sources.append({
            "title": result.get("title", ""),
            "url": url,
            "snippet": result.get("snippet", ""),
            "domain": urlparse(url).netloc,
            "content": _clean_text(text)[:12000] if text else "",
            "fetch_error": fetched.get("error"),
        })

    return {
        "query": query.strip(),
        "source_count": len(sources),
        "sources": sources,
        "research_instruction": (
            "Compare sources, identify agreement and disagreement, "
            "separate facts from claims, and cite source URLs in the final answer."
        ),
    }


def _clean_text(text):
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def build_research_tools(registry):
    registry.register(
        "deep_research",
        "Search multiple public sources, fetch their pages, and return source material for comparison. Arguments: query; max_sources optional.",
        deep_research,
    )
    return registry
