# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`gcloud-selector` is a CLI tool for quickly connecting to Google Cloud VMs via IAP (Identity-Aware Proxy) tunnel. It provides searchable interactive menus, caching, connection history, and favorites. Available as `gcloud-selector` or `gcs` commands.

## Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Test
pytest                              # all tests with coverage
pytest tests/test_config.py         # single test file

# Lint & format
ruff check gcloud_selector
ruff format gcloud_selector

# Type check
mypy gcloud_selector
```

**ruff config:** line-length 100, target py310, rules E/F/W/I/N/UP/B/C4 (ignore E501)
**mypy config:** strict mode — `disallow_untyped_defs`, `warn_return_any`, `warn_unused_ignores`

## Architecture

Four focused modules with clear separation of concerns:

- **`cli.py`** — Entry point (`main()`), argparse, and interactive orchestration. SSH/SCP/port-forward commands are executed via `os.execvp()` to replace the Python process, giving native terminal control to the SSH client.
- **`gcloud.py`** — Wraps `gcloud` CLI subprocess calls; defines dataclasses `Account`, `Project`, `VM`; generates shell commands; raises `GCloudError` / `GCloudNotFoundError` / `GCloudAuthError`.
- **`config.py`** — JSON-file persistence for `Config`, `Cache` (TTL-based), and `History` (max 50 entries). Files live in `~/.config/gcloud-selector/`.
- **`ui.py`** — Terminal menus (`simple-term-menu`), ANSI color formatting, status icons.

### Execution flow

```
main() → parse args → load Config/Cache/History → init GCloud
       → interactive_mode()
           → select_project() [menu]
           → get_vms(project_id) [cached subprocess call]
           → select_vm() [menu]
           → action (SSH/SCP/port-forward) → os.execvp()
```

All GCP state is fetched on-demand from `gcloud` CLI subprocesses; there is no persistent daemon. Cache invalidates on account switches or when TTL (default 300s) expires.

## Key Patterns

- **Dataclasses** for models (`Project`, `VM`, `HistoryEntry`, `Config`) — all include `from_dict()` classmethods for parsing `gcloud --format=json` output.
- **`os.execvp()`** for SSH — replaces the current process rather than spawning a child, so the user's terminal connects directly to the remote shell.
- The legacy `gcloud_selector.py` at the repo root is a standalone initial version; the real package is in `gcloud_selector/`.
- One known TODO: config menu (`--config` flag) is not yet implemented (see `cli.py` line ~441).
