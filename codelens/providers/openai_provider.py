import json
from openai import OpenAI
from .base import BaseProvider, AnalysisResult


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def analyze(self, prompt: str, max_tokens: int) -> AnalysisResult:
        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        raw = response.choices[0].message.content or "{}"
        return _parse_response(raw, self._model, "openai")


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

Return only the JSON object — no markdown fences, no preamble.
"""


def _parse_response(raw: str, model: str, provider: str) -> AnalysisResult:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"summary": raw, "issues": []}

    return AnalysisResult(
        model=model,
        provider=provider,
        issues=data.get("issues", []),
        summary=data.get("summary", ""),
        raw=raw,
    )
