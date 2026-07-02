# Installation Guide

This guide covers all methods of installing GCloud Selector.

## Prerequisites

Before installing GCloud Selector, ensure you have:

### 1. Python 3.10+

Check your Python version:

```bash
python3 --version
```

If you need to install or upgrade Python:

- **macOS**: `brew install python@3.12`
- **Ubuntu/Debian**: `sudo apt install python3.12`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### 2. Google Cloud SDK

The `gcloud` CLI must be installed and configured.

**Install gcloud CLI:**

```bash
# macOS
brew install --cask google-cloud-sdk

# Linux (Debian/Ubuntu)
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
sudo apt-get update && sudo apt-get install google-cloud-cli

# Windows
# Download installer from https://cloud.google.com/sdk/docs/install
```

**Authenticate:**

```bash
gcloud auth login
```

**Verify installation:**

```bash
gcloud --version
gcloud projects list  # Should show your projects
```

### 3. IAP Configuration

Your GCP VMs must have IAP (Identity-Aware Proxy) configured for TCP forwarding. See [Google's IAP documentation](https://cloud.google.com/iap/docs/using-tcp-forwarding).

---

## Installation Methods

### Method 1: pip install (Recommended)

The simplest way to install:

```bash
pip install gcloud-selector
```

This installs the package and creates two commands:
- `gcloud-selector` - Full command name
- `gcs` - Short alias

### Method 2: From Source (Development)

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/yourusername/gcloud-selector.git
cd gcloud-selector

# Create virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install in editable mode
pip install -e .
```

### Method 3: pipx (Isolated Installation)

Using [pipx](https://pypa.github.io/pipx/) for an isolated installation:

```bash
pipx install gcloud-selector
```

### Method 4: From GitHub Releases

Download the latest release:

```bash
pip install https://github.com/yourusername/gcloud-selector/releases/latest/download/gcloud-selector-1.0.0.tar.gz
```

---

## Verifying Installation

After installation, verify everything works:

```bash
# Check version
gcloud-selector --version

# Or using the alias
gcs --version

# Run help
gcs --help
```

You should see:

```
gcloud-selector 1.0.0
```

---

## Platform-Specific Notes

### macOS

If you encounter permission issues:

```bash
# Use user installation
pip install --user gcloud-selector

# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### Linux

Some distributions may require:

```bash
# Install python dev headers (for building dependencies)
sudo apt install python3-dev

# Install pip if missing
sudo apt install python3-pip
```

### Windows

- Use Command Prompt or PowerShell
- The `gcs` alias may conflict with Git for Windows. Use `gcloud-selector` instead.

---

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade gcloud-selector
```

---

## Uninstalling

To remove GCloud Selector:

```bash
pip uninstall gcloud-selector
```

To also remove configuration and cache:

```bash
rm -rf ~/.config/gcloud-selector
```

---

## Next Steps

- [Quick Start Guide](quickstart.md) - Get running in 5 minutes
- [User Guide](user-guide.md) - Complete usage instructions
- [Configuration](configuration.md) - Customize your experience
