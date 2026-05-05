from .base import BaseProvider, AnalysisResult
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from ..config import Config


def build_provider(config: Config) -> BaseProvider:
    if config.provider == "openai":
        return OpenAIProvider(api_key=config.openai_api_key, model=config.resolved_model)
    if config.provider == "anthropic":
        return AnthropicProvider(api_key=config.anthropic_api_key, model=config.resolved_model)
    raise ValueError(f"Unsupported provider: {config.provider}")


__all__ = ["BaseProvider", "AnalysisResult", "OpenAIProvider", "AnthropicProvider", "build_provider"]
