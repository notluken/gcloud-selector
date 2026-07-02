# GCloud Selector Documentation

Welcome to the GCloud Selector documentation. This tool provides an interactive CLI for connecting to Google Cloud Platform VMs via IAP tunnel.

## Table of Contents

1. [Installation Guide](installation.md) - Getting started with GCloud Selector
2. [Quick Start](quickstart.md) - Get up and running in 5 minutes
3. [User Guide](user-guide.md) - Complete usage instructions
4. [Configuration](configuration.md) - Customize your experience
5. [API Reference](api-reference.md) - Developer documentation
6. [Troubleshooting](troubleshooting.md) - Common issues and solutions
7. [Contributing](contributing.md) - How to contribute
8. [Changelog](changelog.md) - Version history

## Overview

GCloud Selector simplifies the process of connecting to GCP VMs by providing:

- **Interactive Selection**: Navigate through projects and VMs with arrow keys
- **Search & Filter**: Quickly find resources in large organizations
- **Connection History**: Fast reconnection to recent VMs
- **Multiple Operations**: SSH, SCP, and port forwarding
- **Caching**: Instant startup on repeated use

## Quick Example

```bash
# Install
pip install gcloud-selector

# Run interactive mode
gcloud-selector

# Or use the short alias
gcs

# Direct connect
gcs -p my-project -v my-vm
```

## Requirements

- Python 3.10+
- Google Cloud SDK (`gcloud` CLI)
- IAP configured for target VMs

## License

MIT License - See [LICENSE](../LICENSE) for details.
