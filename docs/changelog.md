# Changelog

All notable changes to GCloud Selector will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2024-01-28

### Added

- **Interactive Mode**: Arrow-key navigation for project and VM selection
- **Search/Filter**: Press `/` to filter long lists
- **SSH via IAP**: Connect to VMs through Identity-Aware Proxy tunnel
- **SCP Support**: Upload and download files via SCP
- **Port Forwarding**: Set up local-to-remote port forwarding
- **VM Management**: Start and stop VMs from the menu
- **Connection History**: Quick reconnect with `--recent` flag
- **Favorites**: Save favorite VMs for quick access
- **Caching**: Cache project/VM lists for faster startup
- **Configuration**: Customizable settings via config file
- **CLI Arguments**: Direct connection with `-p` and `-v` flags
- **Rich UI**: Color-coded output, status icons, formatted tables

### Configuration Options

- `default_project`: Skip project selection
- `favorites`: List of favorite VMs
- `max_history`: Maximum history entries (default: 50)
- `cache_ttl`: Cache lifetime in seconds (default: 300)
- `cache_enabled`: Enable/disable caching
- `ssh_extra_args`: Additional SSH arguments
- `zone_filter`: Filter VMs by zone
- `show_stopped_vms`: Show/hide stopped VMs

### Commands

- `gcloud-selector` / `gcs`: Main command
- `gcs --recent`: Quick reconnect from history
- `gcs --favorites`: Access favorite VMs
- `gcs -p PROJECT -v VM`: Direct connection
- `gcs --list`: List VMs without connecting
- `gcs --port-forward L:R`: Port forwarding
- `gcs --scp-up FILE`: Upload file
- `gcs --scp-down FILE`: Download file

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | 2024-01-28 | Initial release with full feature set |

[Unreleased]: https://github.com/yourusername/gcloud-selector/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/gcloud-selector/releases/tag/v1.0.0
