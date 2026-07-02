# Quick Start Guide

Get connected to your GCP VMs in under 5 minutes.

## Step 1: Install

```bash
pip install gcloud-selector
```

## Step 2: Authenticate with GCP

If you haven't already:

```bash
gcloud auth login
```

## Step 3: Run

```bash
gcloud-selector
```

Or use the short alias:

```bash
gcs
```

## Step 4: Navigate

You'll see a list of your GCP projects:

```
╔══════════════════════════════════════════════════════════════╗
║  🌩️  GCloud VM Selector                                       ║
║  Connect to GCP VMs via IAP Tunnel                            ║
╚══════════════════════════════════════════════════════════════╝

⏳ Fetching projects...

📁 Select Project:
❯ ★ my-main-project (my-main-project-123)
    staging-project (staging-project-456)
    dev-project (dev-project-789)
```

**Controls:**
| Key | Action |
|-----|--------|
| ↑/↓ | Navigate |
| Enter | Select |
| / | Search/Filter |
| q | Quit |

## Step 5: Select a VM

After selecting a project, you'll see the VMs:

```
💻 Select VM:
   Name                           Zone                      Type            Internal IP
──────────────────────────────────────────────────────────────────────────────────────
❯ 🟢 web-server-1                  us-central1-a             e2-medium       10.128.0.2
  🟢 api-server-1                  us-central1-a             e2-standard-2   10.128.0.3
  🔴 dev-instance                  us-east1-b                e2-micro        10.142.0.5
```

**Status Icons:**
- 🟢 Running
- 🔴 Stopped
- 🟡 Staging/Suspended

## Step 6: Choose an Action

```
🎯 Select Action:
❯ 🔌 SSH Connect          Connect to the VM via SSH through IAP tunnel
  📤 SCP Upload           Upload file to the VM
  📥 SCP Download         Download file from the VM
  🔀 Port Forward         Set up port forwarding to the VM
  ▶️  Start VM             Start a stopped VM
  ⏹️  Stop VM              Stop a running VM
  ℹ️  VM Info              Display detailed VM information
```

## Step 7: Connected!

```
✅ Connecting to web-server-1...

$ gcloud compute ssh web-server-1 --zone=us-central1-a --project=my-project --tunnel-through-iap

Welcome to Ubuntu 22.04.3 LTS
user@web-server-1:~$ 
```

---

## Quick Commands Reference

| Command | Description |
|---------|-------------|
| `gcs` | Interactive mode |
| `gcs --recent` | Connect from history |
| `gcs -p proj -v vm` | Direct connect |
| `gcs -p proj --list` | List VMs |
| `gcs --help` | Show all options |

---

## Next Steps

- Learn all features in the [User Guide](user-guide.md)
- Customize settings in [Configuration](configuration.md)
- Set up [Favorites](user-guide.md#favorites) for frequently used VMs
