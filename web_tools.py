import requests

DEFAULT_TIMEOUT = 15
MAX_RESULTS = 8


def web_search(query, max_results=MAX_RESULTS):
    if not isinstance(query, str) or not query.strip():
        return {"error": "query must be a non-empty string."}
    try:
        response = requests.get(
            "https://www.google.com/search",
            params={"q": query.strip(), "num": min(int(max_results), MAX_RESULTS)},
            headers={"User-Agent": "Kavshara/1.0"},
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except (requests.RequestException, ValueError) as exc:
        return {"error": f"Search failed: {exc}"}

    from html.parser import HTMLParser

    class ResultParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.results = []
            self.current = None

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "a" and attrs.get("href", "").startswith("/url?q="):
                self.current = {"url": attrs["href"][7:].split("&")[0], "title": "", "snippet": ""}

        def handle_data(self, data):
            if self.current:
                if not self.current["title"]:
                    self.current["title"] = data.strip()
                elif data.strip():
                    self.current["snippet"] += data.strip() + " "

        def handle_endtag(self, tag):
            if tag == "a" and self.current:
                if self.current["title"] and self.current["url"]:
                    self.results.append(self.current)
                self.current = None

    parser = ResultParser()
    parser.feed(response.text)
    return {"query": query.strip(), "results": parser.results[:MAX_RESULTS], "count": min(len(parser.results), MAX_RESULTS)}


def fetch_url(url):
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return {"error": "url must start with http:// or https://"}
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Kavshara/1.0"},
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        text = response.text
        return {
            "url": response.url,
            "status": response.status_code,
            "content_type": content_type,
            "content": text[:30000],
            "truncated": len(text) > 30000,
        }
    except requests.RequestException as exc:
        return {"error": f"Fetch failed: {exc}"}


def build_web_tools(registry):
    registry.register(
        "web_search",
        "Search the public web for current information. Argument: query; max_results optional.",
        web_search,
    )
    registry.register(
        "fetch_url",
        "Fetch a public HTTP/HTTPS URL and return its text. Argument: url.",
        fetch_url,
    )
    return registry
