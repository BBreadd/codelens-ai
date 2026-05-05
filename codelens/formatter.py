import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from .providers.base import AnalysisResult

_console = Console()

_SEVERITY_STYLES = {
    "critical": "bold red",
    "warning": "bold yellow",
    "suggestion": "dim cyan",
}

_CATEGORY_ICONS = {
    "bug": "\U0001f41b",
    "security": "\U0001f512",
    "performance": "\u26a1",
    "style": "\U0001f58c\ufe0f",
    "maintainability": "\U0001f9f9",
}


def print_result(label: str | Path, result: AnalysisResult, fmt: str) -> None:
    if fmt == "json":
        _console.print_json(json.dumps({"file": str(label), "result": result.__dict__}))
        return

    _console.print(Panel(f"[bold]{label}[/bold]", expand=False))
    _console.print(f"[dim]Model:[/dim] {result.provider}/{result.model}")
    _console.print(f"\n[italic]{result.summary}[/italic]\n")

    if not result.issues:
        _console.print("[green]\u2713 No issues found.[/green]\n")
        return

    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
    table.add_column("Sev", width=10)
    table.add_column("Category", width=16)
    table.add_column("Line", width=5)
    table.add_column("Description")
    table.add_column("Fix")

    for issue in result.issues:
        sev = issue.get("severity", "?")
        cat = issue.get("category", "")
        icon = _CATEGORY_ICONS.get(cat, "")
        style = _SEVERITY_STYLES.get(sev, "")
        table.add_row(
            f"[{style}]{sev}[/{style}]",
            f"{icon} {cat}",
            str(issue.get("line") or ""),
            issue.get("description", ""),
            issue.get("suggestion", ""),
        )

    _console.print(table)


def print_summary(total_files: int, total_issues: int, cache_hits: int) -> None:
    _console.rule()
    _console.print(
        f"[dim]Analyzed {total_files} file(s) — "
        f"{total_issues} issue(s) found — "
        f"{cache_hits} from cache[/dim]"
    )
