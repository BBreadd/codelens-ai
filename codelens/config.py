import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SUPPORTED_PROVIDERS = ("openai", "anthropic")

PROVIDER_DEFAULTS: dict[str, str] = {
    "openai": "gpt-4o",
    "anthropic": "claude-opus-4-6",
}

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java",
    ".c", ".cpp", ".h", ".cs", ".rb", ".php", ".swift", ".kt",
    ".sh", ".yaml", ".yml", ".json", ".toml",
}

MAX_BYTES_PER_FILE = 64_000


@dataclass
class Config:
    provider: str = field(default_factory=lambda: os.getenv("CODELENS_PROVIDER", "openai"))
    openai_api_key: str | None = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: str | None = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    model: str | None = field(default_factory=lambda: os.getenv("CODELENS_MODEL"))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("CODELENS_MAX_TOKENS", "2048")))
    cache_dir: Path = field(
        default_factory=lambda: Path(os.getenv("CODELENS_CACHE_DIR", "~/.codelens_cache")).expanduser()
    )

    def __post_init__(self) -> None:
        if self.provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unknown provider '{self.provider}'. Choose from: {SUPPORTED_PROVIDERS}")

        if self.provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using the openai provider.")

        if self.provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when using the anthropic provider.")

    @property
    def resolved_model(self) -> str:
        return self.model or PROVIDER_DEFAULTS[self.provider]
