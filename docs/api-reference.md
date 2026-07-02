# API Reference

Developer documentation for the GCloud Selector Python API.

## Module Overview

```
gcloud_selector/
├── __init__.py    # Package metadata
├── cli.py         # Command-line interface
├── config.py      # Configuration management
├── gcloud.py      # GCloud API wrapper
└── ui.py          # Terminal UI components
```

---

## gcloud_selector.gcloud

Core module for interacting with the GCloud CLI.

### Classes

#### `Project`

Represents a GCP project.

```python
from gcloud_selector.gcloud import Project

@dataclass
class Project:
    project_id: str      # The unique project ID
    name: str            # Display name
    project_number: str  # Numeric project identifier
    state: str           # Lifecycle state (ACTIVE, DELETE_REQUESTED, etc.)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create from gcloud JSON response."""
        
    def __str__(self) -> str:
        """Return 'name (project_id)' format."""
```

**Example:**
```python
project = Project(
    project_id="my-project-123",
    name="My Project",
    project_number="123456789",
    state="ACTIVE"
)
print(project)  # "My Project (my-project-123)"
```

---

#### `VM`

Represents a GCP Compute Engine instance.

```python
from gcloud_selector.gcloud import VM

@dataclass
class VM:
    name: str                  # Instance name
    zone: str                  # Zone (e.g., "us-central1-a")
    status: str                # RUNNING, STOPPED, TERMINATED, etc.
    machine_type: str          # e.g., "e2-medium"
    internal_ip: Optional[str] # Internal IP address
    external_ip: Optional[str] # External IP address
    
    @classmethod
    def from_dict(cls, data: dict) -> "VM":
        """Create from gcloud JSON response."""
    
    @property
    def is_running(self) -> bool:
        """Check if VM is running."""
    
    @property
    def status_icon(self) -> str:
        """Get emoji icon for status."""
```

**Status Icons:**
| Status | Icon |
|--------|------|
| RUNNING | 🟢 |
| TERMINATED | 🔴 |
| STOPPED | 🔴 |
| SUSPENDED | 🟡 |
| STAGING | 🟡 |
| PROVISIONING | 🟡 |
| STOPPING | 🟠 |

---

#### `GCloud`

Wrapper for gcloud CLI commands.

```python
from gcloud_selector.gcloud import GCloud

class GCloud:
    def __init__(self, timeout: int = 60):
        """Initialize with command timeout."""
    
    def list_projects(self) -> list[Project]:
        """List all accessible projects."""
    
    def list_vms(
        self, 
        project_id: str,
        zone_filter: Optional[str] = None,
        include_stopped: bool = True
    ) -> list[VM]:
        """List VMs in a project."""
    
    def get_current_project(self) -> Optional[str]:
        """Get the currently configured default project."""
    
    def ssh_command(
        self, 
        vm: VM, 
        project_id: str,
        extra_args: str = ""
    ) -> list[str]:
        """Generate SSH command for a VM."""
    
    def scp_command(
        self,
        vm: VM,
        project_id: str,
        source: str,
        dest: str,
        to_remote: bool = True
    ) -> list[str]:
        """Generate SCP command for file transfer."""
    
    def port_forward_command(
        self,
        vm: VM,
        project_id: str,
        local_port: int,
        remote_port: int
    ) -> list[str]:
        """Generate port forwarding command."""
    
    def start_vm(self, vm: VM, project_id: str) -> bool:
        """Start a stopped VM. Returns success status."""
    
    def stop_vm(self, vm: VM, project_id: str) -> bool:
        """Stop a running VM. Returns success status."""
```

**Example:**
```python
from gcloud_selector.gcloud import GCloud, GCloudError

try:
    gcloud = GCloud(timeout=30)
    
    # List projects
    projects = gcloud.list_projects()
    for p in projects:
        print(f"  - {p.name} ({p.project_id})")
    
    # List VMs in a project
    vms = gcloud.list_vms("my-project", include_stopped=False)
    for vm in vms:
        print(f"  - {vm.status_icon} {vm.name}")
    
    # Generate SSH command
    cmd = gcloud.ssh_command(vms[0], "my-project")
    print(f"Command: {' '.join(cmd)}")

except GCloudError as e:
    print(f"Error: {e}")
```

---

### Exceptions

```python
class GCloudError(Exception):
    """Base exception for gcloud errors."""

class GCloudNotFoundError(GCloudError):
    """gcloud CLI not installed."""

class GCloudAuthError(GCloudError):
    """Authentication issues."""
```

---

## gcloud_selector.config

Configuration, caching, and history management.

### Classes

#### `Config`

Application configuration.

```python
from gcloud_selector.config import Config

@dataclass
class Config:
    default_project: Optional[str] = None
    favorites: list[str] = field(default_factory=list)
    max_history: int = 50
    cache_ttl: int = 300
    cache_enabled: bool = True
    ssh_extra_args: str = ""
    zone_filter: str = ""
    show_stopped_vms: bool = True
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file."""
    
    def save(self):
        """Save configuration to file."""
```

**Example:**
```python
from gcloud_selector.config import Config

# Load config
config = Config.load()

# Modify
config.default_project = "my-project"
config.cache_ttl = 600

# Save
config.save()
```

---

#### `History`

Connection history manager.

```python
from gcloud_selector.config import History, HistoryEntry

@dataclass
class HistoryEntry:
    project: str
    zone: str
    vm_name: str
    timestamp: str
    
    def to_key(self) -> str:
        """Return 'project:zone:vm_name' key."""

class History:
    def __init__(self, max_entries: int = 50):
        """Initialize history manager."""
    
    def add(self, project: str, zone: str, vm_name: str):
        """Add a new history entry."""
    
    def get_recent(self, limit: int = 10) -> list[HistoryEntry]:
        """Get most recent entries."""
    
    def clear(self):
        """Clear all history."""
```

**Example:**
```python
from gcloud_selector.config import History

history = History(max_entries=100)

# Add entry
history.add("my-project", "us-central1-a", "web-server")

# Get recent
recent = history.get_recent(5)
for entry in recent:
    print(f"{entry.vm_name} @ {entry.project}")

# Clear
history.clear()
```

---

#### `Cache`

Simple cache for API responses.

```python
from gcloud_selector.config import Cache

class Cache:
    def __init__(self, ttl: int = 300):
        """Initialize with TTL in seconds."""
    
    def get(self, key: str) -> Optional[any]:
        """Get cached value if not expired."""
    
    def set(self, key: str, data: any):
        """Store value in cache."""
    
    def invalidate(self, key: Optional[str] = None):
        """Invalidate specific key or all cache."""
```

**Example:**
```python
from gcloud_selector.config import Cache

cache = Cache(ttl=300)

# Store data
cache.set("my-key", {"data": "value"})

# Retrieve
data = cache.get("my-key")
if data:
    print(f"Cached: {data}")

# Invalidate
cache.invalidate("my-key")  # Single key
cache.invalidate()          # All cache
```

---

## gcloud_selector.ui

Terminal UI components.

### Functions

#### Display Functions

```python
from gcloud_selector import ui

# Print header
ui.print_header()

# Print status message
ui.print_status("Loading...", "loading")  # info, success, error, warning, loading

# Print section header
ui.print_section("VMs in my-project")

# Ask for confirmation
if ui.confirm("Continue?", default=False):
    print("User confirmed")

# Get text input
value = ui.get_input("Enter name", default="default-value")

# Get port number
port = ui.get_port("Local port", default=8080)

# Display VM info
ui.display_vm_info(vm, "my-project")
```

---

#### Selection Functions

```python
from gcloud_selector import ui

# Select project
project = ui.select_project(projects, current_project="my-project")

# Select VM
vm = ui.select_vm(vms, "my-project")

# Select action
action = ui.select_action()  # Returns: ssh, scp_upload, scp_download, etc.

# Select from history
entry = ui.select_from_history(history_entries)
```

---

#### Colors

```python
from gcloud_selector.ui import Colors

print(f"{Colors.GREEN}Success!{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.CYAN}Header{Colors.RESET}")
```

Available colors:
- `Colors.RESET`
- `Colors.BOLD`, `Colors.DIM`
- `Colors.RED`, `Colors.GREEN`, `Colors.YELLOW`, `Colors.BLUE`, `Colors.MAGENTA`, `Colors.CYAN`, `Colors.WHITE`
- `Colors.BG_CYAN`, `Colors.BG_BLUE`

---

## gcloud_selector.cli

Command-line interface.

### Functions

```python
from gcloud_selector.cli import main, create_parser

# Get argument parser
parser = create_parser()
args = parser.parse_args(["--project", "my-project"])

# Run the CLI
main()  # Entry point
```

---

## Usage Example

Complete example using the API:

```python
#!/usr/bin/env python3
"""Custom script using GCloud Selector API."""

from gcloud_selector.gcloud import GCloud, GCloudError
from gcloud_selector.config import Config, History, Cache
from gcloud_selector import ui

def main():
    # Initialize
    config = Config.load()
    cache = Cache(ttl=config.cache_ttl)
    history = History(max_entries=config.max_history)
    
    try:
        gcloud = GCloud()
    except GCloudError as e:
        ui.print_status(str(e), "error")
        return
    
    # Get projects (with caching)
    cached = cache.get("projects")
    if cached:
        from gcloud_selector.gcloud import Project
        projects = [Project(**p) for p in cached]
    else:
        ui.print_status("Fetching projects...", "loading")
        projects = gcloud.list_projects()
        cache.set("projects", [p.__dict__ for p in projects])
    
    # Select project
    project = ui.select_project(projects)
    if not project:
        return
    
    # Get VMs
    vms = gcloud.list_vms(project.project_id)
    
    # Select VM
    vm = ui.select_vm(vms, project.project_id)
    if not vm:
        return
    
    # Connect
    history.add(project.project_id, vm.zone, vm.name)
    cmd = gcloud.ssh_command(vm, project.project_id)
    
    ui.print_status(f"Connecting to {vm.name}...", "success")
    
    import os
    os.execvp(cmd[0], cmd)

if __name__ == "__main__":
    main()
```

---

## Type Hints

All modules use type hints compatible with Python 3.10+:

```python
from typing import Optional
from gcloud_selector.gcloud import Project, VM

def find_vm(vms: list[VM], name: str) -> Optional[VM]:
    """Find VM by name."""
    return next((v for v in vms if v.name == name), None)
```

---

## Next Steps

- [Contributing Guide](contributing.md)
- [Changelog](changelog.md)
