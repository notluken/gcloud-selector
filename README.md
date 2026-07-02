# GCloud VM Selector

A CLI tool for quickly connecting to Google Cloud VMs through an IAP tunnel — searchable menus, caching, connection history, and favorites, so you never have to remember project IDs or zones again.

![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- 🚀 **Fast** — caching for instant startup on repeated use
- 🔍 **Searchable** — filter through hundreds of projects/VMs by pressing `/`
- 📜 **History** — quick access to recent connections with `--recent`
- ⭐ **Favorites** — save frequently used VMs and jump straight to them with `--favorites`
- 🔌 **Multiple operations** — SSH, SCP upload/download, port forwarding, start/stop
- ⌨️ **CLI arguments** — skip every menu with direct `--project`/`--vm` flags
- ⚙️ **Interactive settings** — edit all configuration from `--config`, no manual JSON editing needed
- 🎨 **Rich UI** — color-coded status, formatted tables, intuitive navigation

## Prerequisites

- Python 3.10+
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and on your `PATH`
- Authenticated with `gcloud auth login`
- [IAP](https://cloud.google.com/iap/docs/using-tcp-forwarding) configured for the VMs you want to reach

## Installation

Install it as a standalone command with [pipx](https://pipx.pypa.io/) so `gcloud-selector`/`gcs` are available in any terminal, without touching your system Python:

```bash
cd gcloud-selector
pipx install -e .
```

The `-e` (editable) flag means any change you make to the source is picked up immediately, without reinstalling.

<details>
<summary>Alternative: plain virtualenv (for local development on the tool itself)</summary>

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

This gives you `gcloud-selector`/`gcs` only while the virtualenv is active.
</details>

Verify it installed correctly:

```bash
gcs --version
```

## Quick Start

```bash
# Interactive mode: pick a project, then a VM, then an action
gcs

# Quick reconnect to a recently used VM
gcs --recent

# Jump straight to a saved favorite
gcs --favorites

# Direct connect, skipping every menu
gcs -p my-project -v my-vm

# List all VMs in a project without connecting
gcs -p my-project --list
```

`gcloud-selector` and `gcs` are the same command — `gcs` is just shorter to type.

## Usage

### Interactive mode

Run it with no arguments for the full guided flow:

```bash
gcs
```

1. **Select a project** — searchable list of every project your account can see (skip with `-p PROJECT`).
2. **Select a VM** — shows status, zone, machine type and internal IP for every VM in the project (skip with `-v VM`, add `-z ZONE` if the name is ambiguous across zones).
3. **Select an action** — a menu appears for the chosen VM:
   - 🔌 **SSH Connect** — opens an SSH session through the IAP tunnel (replaces the current process, so it behaves like a native `ssh`)
   - 📤 **SCP Upload** / 📥 **SCP Download** — transfer a file to/from the VM
   - 🔀 **Port Forward** — forward a local port to a port on the VM
   - ▶️ **Start VM** / ⏹️ **Stop VM** — with a confirmation prompt (hidden if your account lacks the `compute.instances.start`/`stop` permission on that VM)
   - ☆ **Add to Favorites** / ★ **Remove from Favorites** — toggles the VM in your favorites list
   - ℹ️ **VM Info** — prints zone, machine type, internal/external IP, status

**Navigation:**
- **↑/↓** — move through options
- **/** — search/filter the current list
- **Enter** — select
- **q** — quit the current menu

### Direct connection (skip the menus)

```bash
# Connect straight to a specific VM
gcs -p my-project -v my-vm

# Add -z if the same VM name exists in more than one zone
gcs -p my-project -v my-vm -z us-central1-a
```

### File transfer (SCP)

```bash
# Upload a local file
gcs -p my-project -v my-vm --scp-up ./local-file.txt

# Download a remote file
gcs -p my-project -v my-vm --scp-down /remote/path/file.txt
```

### Port forwarding

```bash
# Forward local port 8080 to remote port 80
gcs -p my-project -v my-vm --port-forward 8080:80
```

### Recent connections

Every successful SSH connection is remembered. Reconnect without picking a project/VM again:

```bash
gcs --recent
```

### Favorites

Favorites are a saved shortcut straight to a VM (`project:zone:name`), useful for the machines you connect to constantly across different projects.

**Add a favorite:** select a VM normally, then choose **☆ Add to Favorites** from the action menu.

**Connect from favorites:**

```bash
gcs --favorites
```

This shows only your saved VMs and opens the same action menu (SSH, SCP, start/stop, etc.) — you don't have to reselect the project first.

**Remove a favorite:** either pick it with `-f` and choose **⭐ Remove from Favorites**, or manage the whole list from `--config` (see below).

### Listing VMs

```bash
# Table of all VMs in a project, no connection made
gcs -p my-project --list
```

### Accounts

```bash
# List every authenticated gcloud account
gcs --accounts

# Switch account for this run
gcs -a other-account@example.com

# Pick an account interactively
gcs --select-account
```

## Configuration

Run `gcs --config` to open an interactive settings menu — no manual JSON editing required. From there you can:

- Set a **default project** (skips project selection entirely)
- Toggle **caching** and adjust the **cache TTL**
- Set a **zone filter** to only show VMs in a specific zone
- Toggle whether **stopped VMs** appear in lists
- Add **extra SSH arguments** (e.g. flags for `gcloud compute ssh`)
- Change the **max history** size
- **Manage favorites** — browse and remove saved VMs

Settings persist to `~/.config/gcloud-selector/config.json`:

```json
{
  "default_project": "my-default-project",
  "favorites": [
    "project-1:us-central1-a:vm-1",
    "project-2:europe-west1-b:vm-2"
  ],
  "max_history": 50,
  "cache_ttl": 300,
  "cache_enabled": true,
  "ssh_extra_args": "",
  "zone_filter": "",
  "show_stopped_vms": true
}
```

### Configuration reference

| Option | Description | Default |
|--------|-------------|---------|
| `default_project` | Skip project selection | `null` |
| `favorites` | Saved VMs (`project:zone:name`) | `[]` |
| `max_history` | Maximum history entries | `50` |
| `cache_ttl` | Cache lifetime in seconds | `300` |
| `cache_enabled` | Enable caching | `true` |
| `ssh_extra_args` | Extra arguments passed to the SSH command | `""` |
| `zone_filter` | Only show VMs in this zone | `""` |
| `show_stopped_vms` | Show stopped VMs in lists | `true` |

### Cache and history maintenance

```bash
# Force a fresh fetch from gcloud for one run
gcs --no-cache

# Wipe the project/VM cache (also happens automatically on account switch)
gcs --clear-cache

# Wipe recent-connections history
gcs --clear-history
```

## Command Reference

```
gcloud-selector [OPTIONS]

Connection Options:
  -a, --account EMAIL    Switch to this account
  --select-account       Show account selection menu
  -p, --project TEXT     Project ID (skip project selection)
  -v, --vm TEXT          VM name (skip VM selection, requires --project)
  -z, --zone TEXT        Zone (required if multiple VMs share a name)

Quick Access:
  -r, --recent           Show recent connections
  -f, --favorites        Show favorite VMs

Actions:
  --accounts             List all authenticated accounts
  -l, --list             List VMs without connecting
  --scp-up FILE          Upload file via SCP
  --scp-down FILE        Download file via SCP
  --port-forward L:R     Port forwarding (local:remote)

Configuration:
  --config               Open the interactive configuration menu
  --clear-cache          Clear cached data
  --clear-history        Clear connection history

Debug:
  --verbose              Verbose output
  --debug                Debug logging
  --no-cache             Disable caching for this run
  -V, --version          Show version
```

## Aliases

The package installs two identical commands:
- `gcloud-selector` — full name
- `gcs` — short alias

## Development

```bash
# Install with dev dependencies
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy gcloud_selector

# Linting
ruff check gcloud_selector
```

## Troubleshooting

### "gcloud CLI not found"

Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) and make sure `gcloud` is on your `PATH`.

### "Not authenticated"

Run `gcloud auth login`.

### "IAP tunnel failed"

Make sure IAP is configured for your VM's project and firewall rules. See [Using IAP for TCP forwarding](https://cloud.google.com/iap/docs/using-tcp-forwarding).

### Stale project/VM list after changes in the console

The list is cached for `cache_ttl` seconds (5 minutes by default). Force a refresh with:

```bash
gcs --clear-cache
```

## License

MIT License — see [LICENSE](LICENSE) for details.
