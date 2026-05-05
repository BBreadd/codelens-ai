import hashlib
import json
from pathlib import Path
from typing import Any


class AnalysisCache:
    """
    Filesystem-backed cache keyed on a SHA-256 of (model, prompt_text).
    Prevents redundant API calls for unchanged code.
    """

    def __init__(self, cache_dir: Path) -> None:
        self._dir = cache_dir
        self._dir.mkdir(parents=True, exist_ok=True)

    def _key(self, model: str, content: str) -> str:
        raw = f"{model}:{content}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, model: str, content: str) -> dict[str, Any] | None:
        path = self._dir / self._key(model, content)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, model: str, content: str, result: dict[str, Any]) -> None:
        path = self._dir / self._key(model, content)
        try:
            path.write_text(json.dumps(result, indent=2))
        except OSError:
            pass

    def clear(self) -> int:
        removed = 0
        for entry in self._dir.iterdir():
            if entry.is_file():
                entry.unlink()
                removed += 1
        return removed
