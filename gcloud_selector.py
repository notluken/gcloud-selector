#!/usr/bin/env python3
"""
GCloud VM Selector - A CLI helper for connecting to GCP VMs via IAP tunnel.

This tool provides an interactive interface to:
1. List and select from available GCP projects
2. List and select from available VMs in the chosen project
3. Connect to the selected VM using gcloud compute ssh with --tunnel-through-iap
"""

import subprocess
import sys
import json

try:
    from simple_term_menu import TerminalMenu
except ImportError:
    print("Error: simple-term-menu is required.")
    print("Install it with: pip install simple-term-menu")
    sys.exit(1)


def run_gcloud_command(args: list[str]) -> tuple[bool, str]:
    """Run a gcloud command and return success status and output."""
    try:
        result = subprocess.run(
            ["gcloud"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()
    except FileNotFoundError:
        return False, "gcloud CLI not found. Please install the Google Cloud SDK."


def get_projects() -> list[dict]:
    """Fetch list of projects the user has access to."""
    success, output = run_gcloud_command([
        "projects", "list",
        "--format=json"
    ])
    
    if not success:
        print(f"Error fetching projects: {output}")
        sys.exit(1)
    
    try:
        projects = json.loads(output)
        return projects
    except json.JSONDecodeError:
        print("Error parsing projects response")
        sys.exit(1)


def get_vms(project_id: str) -> list[dict]:
    """Fetch list of VMs in the specified project."""
    success, output = run_gcloud_command([
        "compute", "instances", "list",
        f"--project={project_id}",
        "--format=json"
    ])
    
    if not success:
        print(f"Error fetching VMs: {output}")
        return []
    
    try:
        vms = json.loads(output)
        return vms
    except json.JSONDecodeError:
        print("Error parsing VMs response")
        return []


def select_project(projects: list[dict]) -> dict | None:
    """Display interactive menu to select a project."""
    if not projects:
        print("No projects found.")
        return None
    
    # Create menu items with project name and ID
    menu_items = [
        f"{p.get('name', 'Unknown')} ({p.get('projectId', 'Unknown')})"
        for p in projects
    ]
    
    print("\n🌐 Select a GCP Project:")
    print("  Use ↑/↓ arrows to navigate, Enter to select, q to quit\n")
    
    terminal_menu = TerminalMenu(
        menu_items,
        title="Available Projects:",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("bg_cyan", "fg_black"),
    )
    
    selected_index = terminal_menu.show()
    
    if selected_index is None:
        return None
    
    return projects[selected_index]


def select_vm(vms: list[dict], project_id: str) -> dict | None:
    """Display interactive menu to select a VM."""
    if not vms:
        print(f"\nNo VMs found in project '{project_id}'.")
        return None
    
    # Create menu items with VM name, zone, and status
    menu_items = []
    for vm in vms:
        name = vm.get('name', 'Unknown')
        # Zone is a full URL, extract just the zone name
        zone_full = vm.get('zone', '')
        zone = zone_full.split('/')[-1] if zone_full else 'Unknown'
        status = vm.get('status', 'Unknown')
        
        # Add status indicator
        status_icon = "🟢" if status == "RUNNING" else "🔴"
        menu_items.append(f"{status_icon} {name} ({zone}) - {status}")
    
    print(f"\n💻 Select a VM in project '{project_id}':")
    print("  Use ↑/↓ arrows to navigate, Enter to select, q to quit\n")
    
    terminal_menu = TerminalMenu(
        menu_items,
        title="Available VMs:",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("bg_cyan", "fg_black"),
    )
    
    selected_index = terminal_menu.show()
    
    if selected_index is None:
        return None
    
    return vms[selected_index]


def connect_to_vm(vm: dict, project_id: str):
    """Connect to the selected VM via SSH through IAP tunnel."""
    name = vm.get('name')
    zone_full = vm.get('zone', '')
    zone = zone_full.split('/')[-1] if zone_full else None
    
    if not name or not zone:
        print("Error: Could not determine VM name or zone.")
        sys.exit(1)
    
    print(f"\n🔗 Connecting to '{name}' in zone '{zone}' via IAP tunnel...")
    print("-" * 60)
    
    # Execute the SSH command
    cmd = [
        "gcloud", "compute", "ssh",
        name,
        f"--zone={zone}",
        f"--project={project_id}",
        "--tunnel-through-iap"
    ]
    
    try:
        # Use os.execvp to replace current process with SSH
        import os
        os.execvp("gcloud", cmd)
    except Exception as e:
        print(f"Error connecting to VM: {e}")
        sys.exit(1)


def main():
    """Main entry point for the GCloud Selector."""
    print("=" * 60)
    print("  🌩️  GCloud VM Selector with IAP Tunnel")
    print("=" * 60)
    
    # Step 1: Fetch and select project
    print("\n📋 Fetching available projects...")
    projects = get_projects()
    
    selected_project = select_project(projects)
    if not selected_project:
        print("\nNo project selected. Exiting.")
        sys.exit(0)
    
    project_id = selected_project.get('projectId')
    print(f"\n✅ Selected project: {project_id}")
    
    # Step 2: Fetch and select VM
    print(f"\n📋 Fetching VMs in project '{project_id}'...")
    vms = get_vms(project_id)
    
    selected_vm = select_vm(vms, project_id)
    if not selected_vm:
        print("\nNo VM selected. Exiting.")
        sys.exit(0)
    
    vm_name = selected_vm.get('name')
    print(f"\n✅ Selected VM: {vm_name}")
    
    # Step 3: Connect to VM
    connect_to_vm(selected_vm, project_id)


if __name__ == "__main__":
    main()
