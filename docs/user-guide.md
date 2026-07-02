# User Guide

Complete guide to all GCloud Selector features.

## Table of Contents

1. [Interactive Mode](#interactive-mode)
2. [Command Line Arguments](#command-line-arguments)
3. [SSH Connections](#ssh-connections)
4. [File Transfers (SCP)](#file-transfers-scp)
5. [Port Forwarding](#port-forwarding)
6. [VM Management](#vm-management)
7. [History & Recent Connections](#history--recent-connections)
8. [Favorites](#favorites)
9. [Search & Filtering](#search--filtering)
10. [Keyboard Shortcuts](#keyboard-shortcuts)

---

## Interactive Mode

The default mode provides a full interactive experience with menus and navigation.

```bash
gcloud-selector
# or
gcs
```

### Workflow

1. **Select Project** → Choose from your accessible GCP projects
2. **Select VM** → Choose from VMs in that project
3. **Select Action** → SSH, SCP, Port Forward, etc.
4. **Execute** → The action runs with `--tunnel-through-iap`

### Navigation

| Key | Action |
|-----|--------|
| ↑ / ↓ | Move selection up/down |
| Enter | Confirm selection |
| / | Open search/filter |
| Esc | Cancel search |
| q | Quit/Cancel |

---

## Command Line Arguments

Skip menus by providing arguments directly.

### Basic Syntax

```bash
gcs [OPTIONS] [-p PROJECT] [-v VM] [-z ZONE]
```

### Connection Options

| Argument | Description |
|----------|-------------|
| `-p, --project` | Project ID (skips project selection) |
| `-v, --vm` | VM name (skips VM selection) |
| `-z, --zone` | Zone (required if VM name is ambiguous) |

**Examples:**

```bash
# Connect to specific VM
gcs -p my-project -v my-vm

# Specify zone if multiple VMs have the same name
gcs -p my-project -v web-server -z us-central1-a

# Combined with action
gcs -p my-project -v my-vm --port-forward 8080:80
```

### Quick Access

| Argument | Description |
|----------|-------------|
| `-r, --recent` | Show recent connections |
| `-f, --favorites` | Show favorite VMs |

### Actions

| Argument | Description |
|----------|-------------|
| `-l, --list` | List VMs without connecting |
| `--scp-up FILE` | Upload file via SCP |
| `--scp-down FILE` | Download file via SCP |
| `--port-forward L:R` | Port forwarding (local:remote) |

### Configuration

| Argument | Description |
|----------|-------------|
| `--config` | Show configuration location |
| `--clear-cache` | Clear cached project/VM data |
| `--clear-history` | Clear connection history |

### Debug

| Argument | Description |
|----------|-------------|
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug logging |
| `--no-cache` | Disable caching for this run |
| `-V, --version` | Show version |

---

## SSH Connections

### Interactive SSH

```bash
gcs
# Select project → Select VM → Select "SSH Connect"
```

### Direct SSH

```bash
gcs -p my-project -v my-vm
```

This executes:

```bash
gcloud compute ssh my-vm \
  --zone=us-central1-a \
  --project=my-project \
  --tunnel-through-iap
```

### SSH with Custom Arguments

Configure additional SSH arguments in `~/.config/gcloud-selector/config.json`:

```json
{
  "ssh_extra_args": "-o ServerAliveInterval=60"
}
```

---

## File Transfers (SCP)

### Upload a File

**Interactive:**
```bash
gcs
# Select project → Select VM → Select "SCP Upload"
# Enter local file path
# Enter remote destination
```

**Direct:**
```bash
gcs -p my-project -v my-vm --scp-up ./local-file.txt
```

You'll be prompted for the remote destination (default: `~/filename`).

### Download a File

**Interactive:**
```bash
gcs
# Select project → Select VM → Select "SCP Download"
# Enter remote file path
# Enter local destination
```

**Direct:**
```bash
gcs -p my-project -v my-vm --scp-down /remote/path/file.txt
```

### SCP Commands Generated

Upload:
```bash
gcloud compute scp ./local-file.txt my-vm:~/local-file.txt \
  --zone=us-central1-a \
  --project=my-project \
  --tunnel-through-iap
```

Download:
```bash
gcloud compute scp my-vm:/remote/file.txt ./file.txt \
  --zone=us-central1-a \
  --project=my-project \
  --tunnel-through-iap
```

---

## Port Forwarding

Forward a local port to a remote port on the VM.

### Interactive

```bash
gcs
# Select project → Select VM → Select "Port Forward"
# Enter local port (e.g., 8080)
# Enter remote port (e.g., 80)
```

### Direct

```bash
gcs -p my-project -v my-vm --port-forward 8080:80
```

This forwards `localhost:8080` to `vm:80`.

### Command Generated

```bash
gcloud compute ssh my-vm \
  --zone=us-central1-a \
  --project=my-project \
  --tunnel-through-iap \
  -- -N -L 8080:localhost:80
```

### Use Cases

| Local:Remote | Use Case |
|--------------|----------|
| `8080:80` | Access VM's web server at localhost:8080 |
| `5432:5432` | Connect to PostgreSQL on VM |
| `3306:3306` | Connect to MySQL on VM |
| `6379:6379` | Connect to Redis on VM |
| `27017:27017` | Connect to MongoDB on VM |

---

## VM Management

### Start a VM

From the action menu, select "Start VM" to start a stopped instance.

```
▶️  Start VM
? Start VM 'dev-instance'? [y/N]: y
⏳ Starting VM...
✅ VM started successfully
```

### Stop a VM

From the action menu, select "Stop VM" to stop a running instance.

```
⏹️  Stop VM
? Stop VM 'dev-instance'? [y/N]: y
⏳ Stopping VM...
✅ VM stopped successfully
```

### View VM Info

Select "VM Info" to see detailed information:

```
────────────────────────────────────────────────────────
VM Information: web-server-1
────────────────────────────────────────────────────────

  Project         my-project
  Name            web-server-1
  Zone            us-central1-a
  Status          🟢 RUNNING
  Machine Type    e2-medium
  Internal IP     10.128.0.2
  External IP     34.123.45.67
```

---

## History & Recent Connections

GCloud Selector tracks your connection history for quick reconnection.

### View Recent Connections

```bash
gcs --recent
# or
gcs -r
```

Shows your last 10 connections:

```
📜 Recent Connections:
❯   web-server-1 (my-project) - us-central1-a
    api-server (staging-project) - us-east1-b
    dev-instance (dev-project) - europe-west1-c
```

Select one to reconnect immediately.

### Clear History

```bash
gcs --clear-history
```

### History Storage

History is stored in `~/.config/gcloud-selector/history.json`.

---

## Favorites

Save frequently accessed VMs for quick access.

### Adding Favorites

Edit `~/.config/gcloud-selector/config.json`:

```json
{
  "favorites": [
    "my-project:us-central1-a:web-server-1",
    "staging:us-east1-b:api-server"
  ]
}
```

Format: `project:zone:vm-name`

### Accessing Favorites

```bash
gcs --favorites
# or
gcs -f
```

---

## Search & Filtering

When you have many projects or VMs, use search to filter the list.

### Activating Search

Press `/` to open the search prompt:

```
📁 Select Project:
/web                             # Type to filter
❯ ★ web-project (web-project-123)
    webdev-staging (webdev-456)
```

### Search Tips

- Search is **case-insensitive**
- Matches **anywhere** in the text (name, ID, zone)
- Press **Esc** to clear search
- Press **Enter** to select the highlighted result

---

## Keyboard Shortcuts

### Menu Navigation

| Key | Action |
|-----|--------|
| ↑ / k | Move up |
| ↓ / j | Move down |
| Page Up | Move up 5 items |
| Page Down | Move down 5 items |
| Home | Jump to first item |
| End | Jump to last item |
| Enter | Select item |
| q / Ctrl+C | Quit |

### Search

| Key | Action |
|-----|--------|
| / | Open search |
| Esc | Cancel search |
| Enter | Confirm selection |

### During SSH Session

Standard SSH shortcuts apply:
- `~.` - Disconnect
- `~?` - Show escape help
- `Ctrl+D` - Logout

---

## Next Steps

- [Configuration Reference](configuration.md)
- [Troubleshooting](troubleshooting.md)
- [API Reference](api-reference.md)
