from pathlib import Path
import fnmatch

WORKSPACE = Path("workspace").resolve()

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".venv", "venv",
    "node_modules", ".next", "dist", "build", ".idea", ".vscode"
}
TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".scss",
    ".json", ".md", ".txt", ".yaml", ".yml", ".toml", ".ini", ".env.example"
}
MAX_FILES = 5000
MAX_FILE_SIZE = 1_000_000
MAX_SEARCH_RESULTS = 100
MAX_MATCHES_PER_FILE = 10


def _safe_path(relative_path):
    candidate = (WORKSPACE / relative_path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError("Path must stay inside Kavshara's workspace.")
    return candidate


def _iter_files(root):
    root = _safe_path(root)
    if not root.exists():
        raise ValueError("Path does not exist.")
    if not root.is_dir():
        raise ValueError("Path is not a directory.")

    count = 0
    for path in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path
            count += 1
            if count >= MAX_FILES:
                return


def _file_type(path):
    suffix = path.suffix.lower()
    if suffix in {".py"}:
        return "python"
    if suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return "javascript_typescript"
    if suffix in {".html"}:
        return "html"
    if suffix in {".css", ".scss"}:
        return "styles"
    if suffix in {".json", ".yaml", ".yml", ".toml", ".ini"}:
        return "config"
    if suffix in {".md", ".txt"}:
        return "documentation"
    return "other"


def scan_project(path="."):
    root = _safe_path(path)
    files = []
    total_size = 0

    for file_path in _iter_files(path):
        try:
            size = file_path.stat().st_size
        except OSError:
            continue
        total_size += size
        files.append({
            "path": str(file_path.relative_to(WORKSPACE)),
            "name": file_path.name,
            "type": _file_type(file_path),
            "extension": file_path.suffix.lower(),
            "size": size,
        })

    return {
        "project": str(root.relative_to(WORKSPACE)),
        "file_count": len(files),
        "total_size": total_size,
        "files": files,
        "truncated": len(files) >= MAX_FILES,
    }


def project_summary(path="."):
    root = _safe_path(path)
    result = scan_project(path)
    by_type = {}
    for item in result["files"]:
        by_type[item["type"]] = by_type.get(item["type"], 0) + 1

    important = []
    candidates = [
        "README.md", "pyproject.toml", "requirements.txt", "package.json",
        "tsconfig.json", "vite.config.js", "vite.config.ts",
        "next.config.js", "next.config.ts", "main.py", "app.py", "index.html"
    ]
    for name in candidates:
        candidate = root / name
        if candidate.is_file():
            important.append({
                "path": str(candidate.relative_to(WORKSPACE)),
                "content": _read_small(candidate),
            })

    return {
        "project": str(root.relative_to(WORKSPACE)),
        "file_count": result["file_count"],
        "total_size": result["total_size"],
        "by_type": by_type,
        "important_files": important,
        "truncated": result["truncated"],
    }


def _read_small(path):
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            return "[file too large to preview]"
        return path.read_text(encoding="utf-8", errors="replace")[:12000]
    except OSError as exc:
        return f"[unreadable: {exc}]"


def find_in_project(query, path="."):
    if not isinstance(query, str) or not query.strip():
        return {"error": "query must be a non-empty string"}

    needle = query.lower()
    results = []
    scanned = 0

    for file_path in _iter_files(path):
        if file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            if file_path.stat().st_size > MAX_FILE_SIZE:
                continue
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        scanned += 1
        matches = []
        for line_number, line in enumerate(content.splitlines(), start=1):
            if needle in line.lower():
                matches.append({
                    "line": line_number,
                    "text": line[:500],
                })
                if len(matches) >= MAX_MATCHES_PER_FILE:
                    break

        if matches:
            results.append({
                "path": str(file_path.relative_to(WORKSPACE)),
                "matches": matches,
            })
            if len(results) >= MAX_SEARCH_RESULTS:
                break

    return {
        "query": query,
        "files_scanned": scanned,
        "results": results,
        "truncated": len(results) >= MAX_SEARCH_RESULTS,
    }


def build_project_tools(registry):
    registry.register(
        "scan_project",
        "Recursively map a workspace project. Argument: path optional.",
        scan_project,
    )
    registry.register(
        "project_summary",
        "Summarize a project and preview common entry/config files. Argument: path optional.",
        project_summary,
    )
    registry.register(
        "find_in_project",
        "Search text across project files. Arguments: query, path optional.",
        find_in_project,
    )
    return registry
