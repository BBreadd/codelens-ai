from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class AnalysisResult:
    model: str
    provider: str
    issues: list[dict]
    summary: str
    raw: str


class BaseProvider(ABC):
    """
    Contract that every LLM provider adapter must satisfy.
    Concrete implementations handle API specifics; callers only see this interface.
    """

    @abstractmethod
    def analyze(self, prompt: str, max_tokens: int) -> AnalysisResult:
        """Send a prompt and return a structured AnalysisResult."""
