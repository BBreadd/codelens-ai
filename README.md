# codelens-ai

A command-line tool that runs static analysis on your code using LLMs. Point it at a file, a directory, or pipe a `git diff` through it — it returns structured feedback on bugs, security issues, performance, and style.

Supports OpenAI and Anthropic as interchangeable providers. Results are cached locally by content hash so you don't burn tokens re-analyzing unchanged files.

## Install

```bash
git clone https://github.com/BBreadd/codelens-ai
cd codelens-ai
pip install -e .
```

Copy `.env.example` to `.env` and add your API key.

## Usage

```bash
# Analyze a single file
codelens src/app.py

# Analyze a whole directory
codelens src/ --recursive

# Pipe a git diff
git diff HEAD~1 | codelens

# Export a markdown report
codelens src/ -r --format markdown --output report.md

# Switch providers inline
codelens auth.py --provider anthropic --model claude-opus-4-6
```

Exit code `2` if any critical issue is found — useful for CI pipelines.

## Output formats

| Flag | Description |
|------|-------------|
| `terminal` (default) | Rich-formatted table with color-coded severity |
| `json` | Machine-readable, one JSON blob per file |
| `markdown` | Report file suitable for PRs or wikis |

## Configuration

All settings can be placed in `.env` or passed as env variables:

| Variable | Default | Description |
|---|---|---|
| `CODELENS_PROVIDER` | `openai` | `openai` or `anthropic` |
| `OPENAI_API_KEY` | — | Required for OpenAI |
| `ANTHROPIC_API_KEY` | — | Required for Anthropic |
| `CODELENS_MODEL` | provider default | Override the model |
| `CODELENS_MAX_TOKENS` | `2048` | Max tokens in the response |
| `CODELENS_CACHE_DIR` | `~/.codelens_cache` | Where to store cached results |

## Architecture

```
codelens/
├── cli.py              # Click CLI, orchestration
├── config.py           # Env-driven config with validation
├── cache.py            # SHA-256-keyed filesystem cache
├── reader.py           # File collection, stdin, encoding safety
├── analysis.py         # Prompt builder, sorter, markdown exporter
├── formatter.py        # Rich terminal + JSON output
└── providers/
    ├── base.py         # Abstract BaseProvider + AnalysisResult
    ├── openai_provider.py
    └── anthropic_provider.py
```

Adding a new provider means implementing `BaseProvider.analyze()` and registering it in `providers/__init__.py`.

## License

MIT
