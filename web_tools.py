import ipaddress
import socket
from urllib.parse import urlparse

import requests

DEFAULT_TIMEOUT = 15
MAX_RESULTS = 8
MAX_FETCH_BYTES = 2_000_000

_BLOCKED_HOSTS = {"localhost", "localhost.localdomain"}


def _public_http_url(url):
    if not isinstance(url, str) or not url.strip():
        return None, "url must be a non-empty string."

    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        return None, "Only http:// and https:// URLs are allowed."
    if parsed.username or parsed.password:
        return None, "URLs containing embedded credentials are not allowed."
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        return None, "URL must include a hostname."
    if host in _BLOCKED_HOSTS:
        return None, "Localhost URLs are not allowed for web fetching."

    try:
        addresses = {info[4][0] for info in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)}
    except socket.gaierror:
        return None, "The URL hostname could not be resolved."

    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError:
            continue
        if not ip.is_global:
            return None, "Private, loopback, link-local, or reserved network addresses are not allowed."

    return parsed.geturl(), None


def web_search(query, max_results=MAX_RESULTS):
    if not isinstance(query, str) or not query.strip():
        return {"error": "query must be a non-empty string."}
    try:
        response = requests.get(
            "https://www.google.com/search",
            params={"q": query.strip(), "num": min(max(int(max_results), 1), MAX_RESULTS)},
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
            href = attrs.get("href", "")
            if tag == "a" and href.startswith("/url?q="):
                self.current = {"url": href[7:].split("&")[0], "title": "", "snippet": ""}

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
    return {
        "query": query.strip(),
        "results": parser.results[:MAX_RESULTS],
        "count": min(len(parser.results), MAX_RESULTS),
    }


def fetch_url(url):
    safe_url, error = _public_http_url(url)
    if error:
        return {"error": error}

    try:
        response = requests.get(
            safe_url,
            headers={"User-Agent": "Kavshara/1.0"},
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=True,
            stream=True,
        )
        response.raise_for_status()

        # Validate the final destination too, preventing redirects into local/private networks.
        final_url, final_error = _public_http_url(response.url)
        if final_error:
            response.close()
            return {"error": f"Unsafe redirect destination: {final_error}"}

        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            if not chunk:
                continue
            remaining = MAX_FETCH_BYTES - total
            if remaining <= 0:
                break
            chunk = chunk[:remaining]
            chunks.append(chunk)
            total += len(chunk)
            if total >= MAX_FETCH_BYTES:
                break
        response.close()

        raw = b"".join(chunks)
        encoding = response.encoding or "utf-8"
        text = raw.decode(encoding, errors="replace")
        return {
            "url": final_url,
            "status": response.status_code,
            "content_type": response.headers.get("content-type", ""),
            "content": text[:30000],
            "truncated": total >= MAX_FETCH_BYTES or len(text) > 30000,
        }
    except (requests.RequestException, UnicodeError, ValueError) as exc:
        return {"error": f"Fetch failed: {exc}"}


def build_web_tools(registry):
    registry.register(
        "web_search",
        "Search the public web for current information. Argument: query; max_results optional.",
        web_search,
    )
    registry.register(
        "fetch_url",
        "Fetch a public HTTP/HTTPS URL and return its text. Private, loopback, and reserved network destinations are blocked.",
        fetch_url,
    )
    return registry
