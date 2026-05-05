import sys
from pathlib import Path
from .config import SUPPORTED_EXTENSIONS, MAX_BYTES_PER_FILE


def collect_targets(paths: tuple[Path, ...], recursive: bool) -> list[tuple[Path, str]]:
    """
    Resolve a list of paths into (path, source_code) pairs.
    Skips files that are too large or have unsupported extensions.
    Returns an empty list if no suitable files are found.
    """
    results: list[tuple[Path, str]] = []

    for p in paths:
        if p.is_file():
            entry = _read_file(p)
            if entry:
                results.append(entry)
        elif p.is_dir():
            glob = p.rglob("*") if recursive else p.glob("*")
            for child in sorted(glob):
                if child.is_file():
                    entry = _read_file(child)
                    if entry:
                        results.append(entry)

    return results


def read_stdin() -> str | None:
    if sys.stdin.isatty():
        return None
    return sys.stdin.read()


def _read_file(path: Path) -> tuple[Path, str] | None:
    if path.suffix not in SUPPORTED_EXTENSIONS:
        return None
    try:
        content = path.read_bytes()
    except OSError:
        return None

    if len(content) > MAX_BYTES_PER_FILE:
        return None

    try:
        return path, content.decode("utf-8")
    except UnicodeDecodeError:
        return None
