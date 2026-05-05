import sys
from pathlib import Path

import click
from rich.console import Console

from .config import Config
from .cache import AnalysisCache
from .providers import build_provider
from .reader import collect_targets, read_stdin
from .analysis import build_prompt, sort_issues, write_markdown
from .formatter import print_result, print_summary

console = Console(stderr=True)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option("-r", "--recursive", is_flag=True, help="Recurse into directories.")
@click.option(
    "-f", "--format",
    "fmt",
    type=click.Choice(["terminal", "json", "markdown"]),
    default="terminal",
    show_default=True,
    help="Output format.",
)
@click.option("-o", "--output", type=click.Path(path_type=Path), help="Write output to file (markdown mode).")
@click.option("--no-cache", is_flag=True, help="Skip cache reads and writes.")
@click.option("--clear-cache", is_flag=True, help="Remove all cached results and exit.")
@click.option("--provider", type=str, default=None, help="Override CODELENS_PROVIDER.")
@click.option("--model", type=str, default=None, help="Override CODELENS_MODEL.")
def main(
    paths: tuple[Path, ...],
    recursive: bool,
    fmt: str,
    output: Path | None,
    no_cache: bool,
    clear_cache: bool,
    provider: str | None,
    model: str | None,
) -> None:
    """Analyze code files with an AI model and surface actionable feedback.

    \b
    Accepts file paths, directories, or stdin (piped git diff / file content).

    \b
    Examples:
      codelens src/app.py
      codelens src/ --recursive --format markdown --output report.md
      git diff HEAD~1 | codelens --provider anthropic
    """
    try:
        import os
        if provider:
            os.environ["CODELENS_PROVIDER"] = provider
        if model:
            os.environ["CODELENS_MODEL"] = model
        config = Config()
    except ValueError as exc:
        console.print(f"[red]Configuration error:[/red] {exc}")
        sys.exit(1)

    cache = AnalysisCache(config.cache_dir)

    if clear_cache:
        removed = cache.clear()
        console.print(f"[dim]Cleared {removed} cached result(s).[/dim]")
        return

    stdin_content = read_stdin()
    file_targets = collect_targets(paths, recursive)

    if not stdin_content and not file_targets:
        console.print("[yellow]No input provided. Pass file paths or pipe code via stdin.[/yellow]")
        raise SystemExit(1)

    try:
        provider_instance = build_provider(config)
    except Exception as exc:
        console.print(f"[red]Provider error:[/red] {exc}")
        sys.exit(1)

    all_results = []
    cache_hits = 0

    sources: list[tuple[str | Path, str]] = []
    if stdin_content:
        sources.append(("<stdin>", stdin_content))
    sources.extend(file_targets)

    for label, source in sources:
        prompt = build_prompt(str(label), source)

        cached = None if no_cache else cache.get(config.resolved_model, prompt)

        if cached:
            from .providers.base import AnalysisResult
            result = AnalysisResult(**cached)
            cache_hits += 1
        else:
            try:
                result = provider_instance.analyze(prompt, config.max_tokens)
            except Exception as exc:
                console.print(f"[red]API error for {label}:[/red] {exc}")
                continue

            if not no_cache:
                cache.set(config.resolved_model, prompt, result.__dict__)

        result = sort_issues(result)
        all_results.append((label, result))

    if fmt == "markdown" and output:
        write_markdown(all_results, output)
        console.print(f"[green]Report written to {output}[/green]")
    else:
        for label, result in all_results:
            print_result(label, result, fmt)

    total_issues = sum(len(r.issues) for _, r in all_results)
    print_summary(len(all_results), total_issues, cache_hits)

    if any(
        issue.get("severity") == "critical"
        for _, result in all_results
        for issue in result.issues
    ):
        sys.exit(2)
