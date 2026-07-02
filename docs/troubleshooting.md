# Troubleshooting

Common issues and solutions for GCloud Selector.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Authentication Issues](#authentication-issues)
3. [Connection Issues](#connection-issues)
4. [Performance Issues](#performance-issues)
5. [Display Issues](#display-issues)
6. [Error Messages](#error-messages)

---

## Installation Issues

### "gcloud CLI not found"

**Symptom:**
```
❌ gcloud CLI not found. Please install the Google Cloud SDK.
```

**Solution:**

1. Install the Google Cloud SDK:
   ```bash
   # macOS
   brew install --cask google-cloud-sdk
   
   # Linux
   curl https://sdk.cloud.google.com | bash
   
   # Reload shell
   exec -l $SHELL
   ```

2. Verify installation:
   ```bash
   gcloud --version
   ```

3. Add to PATH if needed:
   ```bash
   export PATH="$HOME/google-cloud-sdk/bin:$PATH"
   ```

---

### "simple-term-menu not found"

**Symptom:**
```
ModuleNotFoundError: No module named 'simple_term_menu'
```

**Solution:**

```bash
pip install simple-term-menu>=1.6.0
```

Or reinstall gcloud-selector:
```bash
pip install --force-reinstall gcloud-selector
```

---

### "Permission denied"

**Symptom:**
```
ERROR: Could not install packages due to an OSError: Permission denied
```

**Solution:**

Use user installation:
```bash
pip install --user gcloud-selector
```

Or use a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install gcloud-selector
```

---

## Authentication Issues

### "Not authenticated"

**Symptom:**
```
❌ Not authenticated. Run 'gcloud auth login' first.
```

**Solution:**

1. Authenticate with GCP:
   ```bash
   gcloud auth login
   ```

2. Follow the browser flow to complete authentication.

3. Verify:
   ```bash
   gcloud projects list
   ```

---

### "No projects found"

**Symptom:**
The project list is empty even though you have projects.

**Possible causes:**

1. **Wrong account**: You may be authenticated with a different account.
   ```bash
   gcloud auth list
   gcloud config set account your-email@example.com
   ```

2. **Missing permissions**: Ensure you have `resourcemanager.projects.list` permission.

3. **Organization restrictions**: Your organization may restrict project visibility.

---

### "Permission denied" on project

**Symptom:**
```
ERROR: (gcloud.compute.instances.list) Permission denied
```

**Solution:**

Ensure you have the required IAM roles:
- `Compute Viewer` (to list VMs)
- `IAP-secured Tunnel User` (to use IAP)

Contact your GCP administrator to grant access.

---

## Connection Issues

### "IAP tunnel failed"

**Symptom:**
```
ERROR: (gcloud.compute.ssh) Could not connect to IAP tunnel.
```

**Possible causes and solutions:**

1. **IAP not enabled**:
   - Go to GCP Console → Security → Identity-Aware Proxy
   - Enable IAP for the VM's project

2. **Firewall rules missing**:
   - Create firewall rule allowing TCP from `35.235.240.0/20` (IAP IP range)
   - Target: VM's network tags or all instances
   - Port: 22 (SSH)

3. **VM not running**:
   ```bash
   gcs -p my-project --list  # Check VM status
   ```
   Start the VM if it's stopped.

4. **Network issues**:
   - Check if your network blocks outbound connections
   - Try from a different network

---

### "Connection timed out"

**Symptom:**
Connection hangs and eventually times out.

**Solutions:**

1. **Check VM status**: Ensure the VM is running.

2. **Check SSH daemon**: The VM may have SSH disabled.
   - Use serial console via GCP Console to check

3. **Increase gcloud timeout**:
   ```bash
   gcloud config set compute/connect_timeout 60
   ```

4. **Check for load**: The VM may be overloaded.

---

### "Host key verification failed"

**Symptom:**
```
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

**Solution:**

Remove the old host key:
```bash
ssh-keygen -R compute.<instance-id>
```

Or add to config (less secure):
```json
{
  "ssh_extra_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
}
```

---

## Performance Issues

### "Slow startup"

**Symptom:**
Takes several seconds before showing the menu.

**Solutions:**

1. **Enable caching** (default):
   ```json
   {
     "cache_enabled": true,
     "cache_ttl": 300
   }
   ```

2. **Clear stale cache**:
   ```bash
   gcs --clear-cache
   ```

3. **Use direct connection**:
   ```bash
   gcs -p my-project -v my-vm  # Skip menus
   ```

---

### "Many projects/VMs loading slowly"

**Solution:**

1. **Use zone filter** to reduce VMs:
   ```json
   {
     "zone_filter": "us-central1-a,us-central1-b"
   }
   ```

2. **Hide stopped VMs**:
   ```json
   {
     "show_stopped_vms": false
   }
   ```

3. **Set default project**:
   ```json
   {
     "default_project": "my-main-project"
   }
   ```

---

## Display Issues

### "Menu looks garbled"

**Symptom:**
Characters display incorrectly or menus don't align.

**Solutions:**

1. **Use a proper terminal emulator**:
   - macOS: iTerm2, Terminal.app
   - Linux: GNOME Terminal, Konsole
   - Windows: Windows Terminal, PowerShell

2. **Set UTF-8 encoding**:
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

3. **Use a monospace font** with emoji support.

---

### "Colors not showing"

**Symptom:**
Output is plain text without colors.

**Solutions:**

1. **Enable color support**:
   ```bash
   export TERM=xterm-256color
   ```

2. **Check terminal**: Some terminals (like basic cmd.exe) don't support ANSI colors.

---

### "Arrow keys not working"

**Symptom:**
Arrow keys type `^[[A` instead of navigating.

**Solutions:**

1. **Use a proper terminal**: Raw SSH or basic terminals may not support arrow keys.

2. **Use vim-style keys**: `j` (down) and `k` (up) also work.

---

## Error Messages

### Common Errors Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `gcloud CLI not found` | SDK not installed | Install Google Cloud SDK |
| `Not authenticated` | No active login | Run `gcloud auth login` |
| `No projects found` | No access or wrong account | Check IAM permissions |
| `No VMs found` | Empty project or no access | Check project has VMs |
| `Could not connect to IAP` | IAP not configured | Enable IAP for project |
| `Connection timed out` | VM not accessible | Check VM status & firewall |
| `Permission denied` | Insufficient IAM roles | Request required permissions |
| `Command timed out` | Slow network or API | Increase timeout, retry |

---

## Debug Mode

For detailed troubleshooting, enable debug logging:

```bash
gcs --debug
```

This shows:
- API calls being made
- Command execution
- Cache hits/misses
- Timing information

---

## Getting Help

If your issue isn't listed here:

1. **Check the logs**:
   ```bash
   gcs --debug 2>&1 | tee debug.log
   ```

2. **Open an issue** on GitHub with:
   - Your OS and Python version
   - GCloud SDK version (`gcloud --version`)
   - Debug log output
   - Steps to reproduce

3. **Check existing issues** for similar problems.

---

## Next Steps

- [User Guide](user-guide.md)
- [Configuration](configuration.md)
- [API Reference](api-reference.md)
