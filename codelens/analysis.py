from pathlib import Path
from .providers.base import AnalysisResult

_SEVERITY_ORDER = {"critical": 0, "warning": 1, "suggestion": 2}


def build_prompt(label: str, source: str) -> str:
    return f"""Analyze the following code from `{label}`:\n\n```\n{source}\n```"""


def sort_issues(result: AnalysisResult) -> AnalysisResult:
    result.issues.sort(key=lambda i: _SEVERITY_ORDER.get(i.get("severity", "suggestion"), 99))
    return result


def write_markdown(results: list[tuple[Path | str, AnalysisResult]], output_path: Path) -> None:
    lines = ["# CodeLens Analysis Report\n"]

    for label, result in results:
        lines.append(f"## `{label}`\n")
        lines.append(f"**Model:** {result.provider}/{result.model}  \n")
        lines.append(f"**Summary:** {result.summary}\n")

        if result.issues:
            lines.append("### Issues\n")
            for issue in result.issues:
                sev = issue.get("severity", "?").upper()
                cat = issue.get("category", "")
                line_ref = f" (line {issue['line']})" if issue.get("line") else ""
                lines.append(f"**[{sev}] {cat}{line_ref}**  ")
                lines.append(f"{issue.get('description', '')}  ")
                lines.append(f"*Fix:* {issue.get('suggestion', '')}\n")
        else:
            lines.append("No issues found.\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
