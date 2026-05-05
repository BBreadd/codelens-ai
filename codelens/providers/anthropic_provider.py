import json
import anthropic
from .base import BaseProvider, AnalysisResult


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def analyze(self, prompt: str, max_tokens: int) -> AnalysisResult:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text if message.content else "{}"
        return _parse_response(raw, self._model, "anthropic")


_SYSTEM_PROMPT = """
You are an expert code reviewer. Analyze the provided code and return a JSON object
with exactly this shape:

{
  "summary": "<one paragraph overview of the code quality>",
  "issues": [
    {
      "severity": "critical" | "warning" | "suggestion",
      "category": "bug" | "security" | "performance" | "style" | "maintainability",
      "line": <line number or null>,
      "description": "<concise description>",
      "suggestion": "<concrete fix or improvement>"
    }
  ]
}

Return only the JSON object, no markdown fences, no preamble.
"""


def _parse_response(raw: str, model: str, provider: str) -> AnalysisResult:
    clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
    try:
        data = json.loads(clean)
    except json.JSONDecodeError:
        data = {"summary": raw, "issues": []}

    return AnalysisResult(
        model=model,
        provider=provider,
        issues=data.get("issues", []),
        summary=data.get("summary", ""),
        raw=raw,
    )
