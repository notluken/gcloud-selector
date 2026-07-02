# Configuration Reference

Complete reference for all configuration options.

## Configuration File Location

```
~/.config/gcloud-selector/config.json
```

On different systems:
- **macOS**: `~/.config/gcloud-selector/config.json`
- **Linux**: `~/.config/gcloud-selector/config.json`
- **Windows**: `C:\Users\<username>\.config\gcloud-selector\config.json`

## File Structure

The configuration directory contains:

```
~/.config/gcloud-selector/
├── config.json     # Main configuration
├── cache.json      # Cached API responses
└── history.json    # Connection history
```

## Default Configuration

When first run, GCloud Selector creates a default configuration:

```json
{
  "default_project": null,
  "favorites": [],
  "max_history": 50,
  "cache_ttl": 300,
  "cache_enabled": true,
  "ssh_extra_args": "",
  "zone_filter": "",
  "show_stopped_vms": true
}
```

---

## Configuration Options

### default_project

**Type:** `string | null`

Pre-select a project to skip the project selection menu.

```json
{
  "default_project": "my-main-project"
}
```

**Behavior:**
- If set, skips project selection and jumps directly to VM selection
- If the project doesn't exist or you don't have access, falls back to selection

---

### favorites

**Type:** `array[string]`

List of favorite VMs for quick access with `--favorites`.

```json
{
  "favorites": [
    "my-project:us-central1-a:web-server",
    "staging-project:europe-west1-b:api-server",
    "dev-project:us-east1-c:dev-instance"
  ]
}
```

**Format:** `project-id:zone:vm-name`

**Usage:**
```bash
gcs --favorites
```

---

### max_history

**Type:** `integer`

Maximum number of connection history entries to keep.

```json
{
  "max_history": 50
}
```

**Default:** `50`

**Notes:**
- Older entries are automatically removed when the limit is reached
- Set to `0` to disable history tracking

---

### cache_ttl

**Type:** `integer`

Cache time-to-live in seconds.

```json
{
  "cache_ttl": 300
}
```

**Default:** `300` (5 minutes)

**Notes:**
- Cached data includes project list and VMs
- Set to `0` to always fetch fresh data
- Clear cache manually with `gcs --clear-cache`

---

### cache_enabled

**Type:** `boolean`

Enable or disable caching.

```json
{
  "cache_enabled": true
}
```

**Default:** `true`

**Notes:**
- Disable for testing or if data changes frequently
- Can be temporarily disabled with `--no-cache` flag

---

### ssh_extra_args

**Type:** `string`

Additional arguments to pass to `gcloud compute ssh`.

```json
{
  "ssh_extra_args": "-o ServerAliveInterval=60 -o ServerAliveCountMax=3"
}
```

**Default:** `""` (empty)

**Common options:**

| Option | Description |
|--------|-------------|
| `-o ServerAliveInterval=60` | Keep connection alive |
| `-o StrictHostKeyChecking=no` | Don't verify host key |
| `-o UserKnownHostsFile=/dev/null` | Don't save host key |
| `-A` | Enable SSH agent forwarding |
| `-L 8080:localhost:80` | Local port forwarding |
| `-R 9000:localhost:22` | Remote port forwarding |

---

### zone_filter

**Type:** `string`

Filter VMs by zone.

```json
{
  "zone_filter": "us-central1-a,us-central1-b"
}
```

**Default:** `""` (show all zones)

**Examples:**
- `"us-central1-a"` - Single zone
- `"us-central1-a,us-east1-b"` - Multiple zones
- `"us-*"` - Wildcard (not supported, use multiple zones)

---

### show_stopped_vms

**Type:** `boolean`

Whether to show stopped VMs in the list.

```json
{
  "show_stopped_vms": true
}
```

**Default:** `true`

**Notes:**
- Set to `false` to only show running VMs
- Stopped VMs can still be selected but require starting before SSH

---

## Example Configurations

### Minimal (Power User)

Skip project selection, hide stopped VMs:

```json
{
  "default_project": "my-main-project",
  "show_stopped_vms": false
}
```

### Organization Admin

Long cache, many history entries:

```json
{
  "max_history": 200,
  "cache_ttl": 600,
  "favorites": [
    "prod:us-central1-a:bastion",
    "staging:us-central1-a:jump-host"
  ]
}
```

### Security Focused

No history, connection keep-alive:

```json
{
  "max_history": 0,
  "ssh_extra_args": "-o ServerAliveInterval=60"
}
```

### Development

No caching, show all VMs:

```json
{
  "cache_enabled": false,
  "show_stopped_vms": true
}
```

---

## Environment Variables

Currently, GCloud Selector doesn't use environment variables. All configuration is file-based.

However, the underlying `gcloud` CLI respects standard GCP environment variables:

| Variable | Description |
|----------|-------------|
| `CLOUDSDK_CORE_PROJECT` | Default project |
| `CLOUDSDK_COMPUTE_ZONE` | Default zone |
| `CLOUDSDK_COMPUTE_REGION` | Default region |

---

## Cache Management

### View Cache Location

```bash
ls ~/.config/gcloud-selector/cache.json
```

### Clear Cache

```bash
gcs --clear-cache
```

### Cache Contents

The cache stores:
- Project list (key: `projects`)
- VM list per project (key: `vms:<project-id>`)

Each entry includes:
- `data`: The cached response
- `timestamp`: When it was cached

---

## History Management

### View History

```bash
cat ~/.config/gcloud-selector/history.json
```

### Clear History

```bash
gcs --clear-history
```

### History Entry Format

```json
{
  "project": "my-project",
  "zone": "us-central1-a",
  "vm_name": "web-server",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

---

## Troubleshooting

### Config Not Loading

Check file permissions:
```bash
ls -la ~/.config/gcloud-selector/
```

Verify JSON syntax:
```bash
python3 -m json.tool ~/.config/gcloud-selector/config.json
```

### Reset to Defaults

Remove the config file:
```bash
rm ~/.config/gcloud-selector/config.json
```

A new default config will be created on next run.

---

## Next Steps

- [User Guide](user-guide.md)
- [Troubleshooting](troubleshooting.md)
- [API Reference](api-reference.md)
