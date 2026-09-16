"""Command-line interface for GCloud Selector."""

import argparse
import logging
import os
import sys
from typing import Optional

from . import __version__
from .config import Config, History, Cache, CONFIG_FILE
from .gcloud import GCloud, GCloudError, GCloudNotFoundError, GCloudAuthError, VM
from . import ui


def setup_logging(verbose: bool = False, debug: bool = False):
    """Configure logging."""
    level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="gcloud-selector",
        description="Interactive CLI for connecting to GCP VMs via IAP tunnel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gcloud-selector                    # Interactive mode
  gcloud-selector -p my-project      # Pre-select project
  gcloud-selector --recent           # Quick connect from history
  gcloud-selector --favorites        # Quick connect from favorites
  gcloud-selector --list             # List all VMs across projects
  gcloud-selector -p proj -v my-vm   # Direct connect to specific VM
  gcloud-selector --config           # Manage settings and favorites
        """
    )
    
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    # Connection options
    conn_group = parser.add_argument_group("Connection Options")
    conn_group.add_argument(
        "-a", "--account",
        help="Account email (switch to this account)"
    )
    conn_group.add_argument(
        "--select-account",
        action="store_true",
        help="Show account selection menu"
    )
    conn_group.add_argument(
        "-p", "--project",
        help="Project ID (skip project selection)"
    )
    conn_group.add_argument(
        "-v", "--vm",
        help="VM name (skip VM selection, requires --project)"
    )
    conn_group.add_argument(
        "-z", "--zone",
        help="Zone (required if multiple VMs have the same name)"
    )
    
    # Quick access
    quick_group = parser.add_argument_group("Quick Access")
    quick_group.add_argument(
        "-r", "--recent",
        action="store_true",
        help="Show recent connections for quick access"
    )
    quick_group.add_argument(
        "-f", "--favorites",
        action="store_true",
        help="Show favorite VMs"
    )
    
    # Actions
    action_group = parser.add_argument_group("Actions")
    action_group.add_argument(
        "--accounts",
        action="store_true",
        help="List all authenticated accounts"
    )
    action_group.add_argument(
        "-l", "--list",
        action="store_true",
        help="List VMs without connecting"
    )
    action_group.add_argument(
        "--scp-up",
        metavar="FILE",
        help="Upload file via SCP"
    )
    action_group.add_argument(
        "--scp-down",
        metavar="FILE",
        help="Download file via SCP"
    )
    action_group.add_argument(
        "--port-forward",
        metavar="LOCAL[:HOST]:REMOTE",
        help="Set up port forwarding (e.g., 8080:80 or 8080:10.0.0.5:80; host defaults to 127.0.0.1)"
    )
    
    # Configuration
    config_group = parser.add_argument_group("Configuration")
    config_group.add_argument(
        "--config",
        action="store_true",
        help="Open configuration menu"
    )
    config_group.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear cached data"
    )
    config_group.add_argument(
        "--clear-history",
        action="store_true",
        help="Clear connection history"
    )
    
    # Debug options
    debug_group = parser.add_argument_group("Debug Options")
    debug_group.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    debug_group.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    debug_group.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching"
    )
    
    return parser


def get_projects(gcloud: GCloud, cache: Cache, use_cache: bool = True):
    """Get projects with optional caching."""
    cache_key = "projects"
    
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            from .gcloud import Project
            return [Project(**p) for p in cached]
    
    ui.print_status("Fetching projects...", "loading")
    projects = gcloud.list_projects()
    
    if use_cache and projects:
        cache.set(cache_key, [p.__dict__ for p in projects])
    
    return projects


def get_vms(gcloud: GCloud, project_id: str, config: Config, 
            cache: Cache, use_cache: bool = True):
    """Get VMs with optional caching."""
    cache_key = f"vms:{project_id}"
    
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            from .gcloud import VM
            return [VM(**v) for v in cached]
    
    ui.print_status(f"Fetching VMs in {project_id}...", "loading")
    vms = gcloud.list_vms(
        project_id,
        zone_filter=config.zone_filter or None,
        include_stopped=config.show_stopped_vms
    )
    
    if use_cache and vms:
        cache.set(cache_key, [v.__dict__ for v in vms])

    return vms


def get_start_stop_permissions(gcloud: GCloud, vm: VM, project_id: str,
                               cache: Cache, use_cache: bool = True) -> tuple[bool, bool]:
    """Check whether the active account can start/stop this VM, with caching."""
    cache_key = f"perms:{project_id}:{vm.zone}:{vm.name}"

    if use_cache:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached["can_start"], cached["can_stop"]

    granted = gcloud.test_permissions(
        vm, project_id, ["compute.instances.start", "compute.instances.stop"]
    )
    can_start = "compute.instances.start" in granted
    can_stop = "compute.instances.stop" in granted

    if use_cache:
        cache.set(cache_key, {"can_start": can_start, "can_stop": can_stop})

    return can_start, can_stop


def connect_ssh(gcloud: GCloud, vm: VM, project_id: str, 
                config: Config, history: History):
    """Connect to VM via SSH."""
    # Add to history
    history.add(project_id, vm.zone, vm.name)
    
    # Generate and execute command
    cmd = gcloud.ssh_command(vm, project_id, config.ssh_extra_args)
    
    ui.print_status(f"Connecting to {vm.name}...", "success")
    print(f"\n{ui.Colors.DIM}$ {' '.join(cmd)}{ui.Colors.RESET}\n")
    
    # Replace current process with SSH
    os.execvp(cmd[0], cmd)


def handle_port_forward(gcloud: GCloud, vm: VM, project_id: str, 
                        port_spec: Optional[str] = None):
    """Handle port forwarding action."""
    host = "127.0.0.1"

    if port_spec:
        parts = port_spec.split(":")
        try:
            if len(parts) == 2:
                local, remote = int(parts[0]), int(parts[1])
            elif len(parts) == 3:
                local, host, remote = int(parts[0]), parts[1], int(parts[2])
                if not host:
                    raise ValueError
            else:
                raise ValueError
        except ValueError:
            ui.print_status(
                "Invalid port format. Use LOCAL:REMOTE or LOCAL:HOST:REMOTE "
                "(e.g., 8080:80 or 8080:10.0.0.5:80)",
                "error"
            )
            return
    else:
        local = ui.get_port("Local port", 8080)
        remote = ui.get_port("Remote port", 80)
        if not local or not remote:
            return
        host = ui.get_input("Remote host", "127.0.0.1")

    cmd = gcloud.port_forward_command(vm, project_id, local, remote, host)

    ui.print_status(
        f"Port forwarding localhost:{local} -> {vm.name}:{host}:{remote}", "success"
    )
    print(f"\n{ui.Colors.DIM}$ {' '.join(cmd)}{ui.Colors.RESET}\n")
    print(f"{ui.Colors.YELLOW}Press Ctrl+C to stop port forwarding{ui.Colors.RESET}\n")
    
    os.execvp(cmd[0], cmd)


def handle_scp(gcloud: GCloud, vm: VM, project_id: str, 
               file_path: str, upload: bool = True):
    """Handle SCP upload/download."""
    if upload:
        if not os.path.exists(file_path):
            ui.print_status(f"File not found: {file_path}", "error")
            return
        dest = ui.get_input("Remote destination path", f"~/{os.path.basename(file_path)}")
        cmd = gcloud.scp_command(vm, project_id, file_path, dest, to_remote=True)
        action = "Uploading"
    else:
        dest = ui.get_input("Local destination path", f"./{os.path.basename(file_path)}")
        cmd = gcloud.scp_command(vm, project_id, file_path, dest, to_remote=False)
        action = "Downloading"
    
    ui.print_status(f"{action} {file_path}...", "loading")
    print(f"\n{ui.Colors.DIM}$ {' '.join(cmd)}{ui.Colors.RESET}\n")
    
    os.execvp(cmd[0], cmd)


def handle_action(action: Optional[str], gcloud: GCloud, vm: VM, project_id: str,
                  config: Config, history: History):
    """Execute the action selected from the VM action menu."""
    if action == "ssh":
        connect_ssh(gcloud, vm, project_id, config, history)
    elif action == "scp_upload":
        file_path = ui.get_input("Local file to upload")
        if file_path:
            handle_scp(gcloud, vm, project_id, file_path, upload=True)
    elif action == "scp_download":
        file_path = ui.get_input("Remote file to download")
        if file_path:
            handle_scp(gcloud, vm, project_id, file_path, upload=False)
    elif action == "port_forward":
        handle_port_forward(gcloud, vm, project_id)
    elif action == "start":
        if vm.is_running:
            ui.print_status("VM is already running", "warning")
        elif ui.confirm(f"Start VM '{vm.name}'?"):
            ui.print_status("Starting VM...", "loading")
            if gcloud.start_vm(vm, project_id):
                ui.print_status("VM started successfully", "success")
            else:
                ui.print_status("Failed to start VM", "error")
    elif action == "stop":
        if not vm.is_running:
            ui.print_status("VM is not running", "warning")
        elif ui.confirm(f"Stop VM '{vm.name}'?"):
            ui.print_status("Stopping VM...", "loading")
            if gcloud.stop_vm(vm, project_id):
                ui.print_status("VM stopped successfully", "success")
            else:
                ui.print_status("Failed to stop VM", "error")
    elif action == "favorite":
        config.add_favorite(project_id, vm.zone, vm.name)
        ui.print_status(f"Added '{vm.name}' to favorites", "success")
    elif action == "unfavorite":
        config.remove_favorite(project_id, vm.zone, vm.name)
        ui.print_status(f"Removed '{vm.name}' from favorites", "success")
    elif action == "info":
        ui.display_vm_info(vm, project_id)


def handle_favorites_menu(config: Config):
    """Interactively review and remove favorite VMs."""
    while True:
        selected = ui.select_from_favorites(config.favorites)
        if not selected:
            return
        project_id, zone, vm_name = selected
        if ui.confirm(f"Remove '{vm_name}' ({project_id}/{zone}) from favorites?"):
            config.remove_favorite(project_id, zone, vm_name)
            ui.print_status("Removed from favorites", "success")


def handle_config_menu(config: Config):
    """Interactive configuration menu (--config)."""
    ui.print_status(f"Config file: {CONFIG_FILE}", "info")

    while True:
        choice = ui.select_config_menu(config)
        if choice is None:
            return

        if choice == "favorites":
            handle_favorites_menu(config)
            continue
        elif choice == "default_project":
            value = ui.get_input("Default project ID (empty to clear)", config.default_project or "")
            config.default_project = value or None
        elif choice == "cache_enabled":
            config.cache_enabled = not config.cache_enabled
        elif choice == "cache_ttl":
            value = ui.get_input("Cache TTL in seconds", str(config.cache_ttl))
            if not value.isdigit():
                ui.print_status("Invalid number", "error")
                continue
            config.cache_ttl = int(value)
        elif choice == "zone_filter":
            config.zone_filter = ui.get_input("Zone filter (empty = all zones)", config.zone_filter)
        elif choice == "show_stopped_vms":
            config.show_stopped_vms = not config.show_stopped_vms
        elif choice == "ssh_extra_args":
            config.ssh_extra_args = ui.get_input("Extra SSH arguments", config.ssh_extra_args)
        elif choice == "max_history":
            value = ui.get_input("Max history entries", str(config.max_history))
            if not value.isdigit():
                ui.print_status("Invalid number", "error")
                continue
            config.max_history = int(value)

        config.save()
        ui.print_status("Configuration saved", "success")


def interactive_mode(gcloud: GCloud, config: Config, cache: Cache,
                     history: History, args):
    """Run interactive selection mode."""
    use_cache = config.cache_enabled and not args.no_cache
    
    # Handle account selection/switching
    if args.select_account or args.account:
        if args.account:
            # Direct account switch
            if gcloud.set_account(args.account):
                ui.print_status(f"Switched to account: {args.account}", "success")
                # Invalidate cache since account changed
                cache.invalidate()
            else:
                ui.print_status(f"Failed to switch to account: {args.account}", "error")
                return
        else:
            # Interactive account selection
            ui.print_status("Fetching accounts...", "loading")
            accounts = gcloud.list_accounts()
            current_account = gcloud.get_active_account()
            
            if len(accounts) <= 1:
                ui.print_status("Only one account available.", "info")
            else:
                selected_account = ui.select_account(accounts, current_account)
                if not selected_account:
                    ui.print_status("No account selected. Exiting.", "info")
                    return
                
                if selected_account.email != current_account:
                    if gcloud.set_account(selected_account.email):
                        ui.print_status(f"Switched to: {selected_account.email}", "success")
                        # Invalidate cache since account changed
                        cache.invalidate()
                    else:
                        ui.print_status("Failed to switch account", "error")
                        return
    
    # Handle recent connections
    if args.recent:
        recent = history.get_recent(10)
        entry = ui.select_from_history(recent)
        if entry:
            # Fetch VM details and connect
            vms = get_vms(gcloud, entry.project, config, cache, use_cache)
            vm = next((v for v in vms if v.name == entry.vm_name and v.zone == entry.zone), None)
            if vm:
                connect_ssh(gcloud, vm, entry.project, config, history)
                return
            else:
                ui.print_status(f"VM {entry.vm_name} not found in project {entry.project}", "error")
        return

    # Handle favorite VMs
    if args.favorites:
        fav_selected = ui.select_from_favorites(config.favorites)
        if not fav_selected:
            return
        fav_project_id, fav_zone, fav_vm_name = fav_selected
        vms = get_vms(gcloud, fav_project_id, config, cache, use_cache)
        vm = next((v for v in vms if v.name == fav_vm_name and v.zone == fav_zone), None)
        if not vm:
            ui.print_status(f"VM {fav_vm_name} not found in project {fav_project_id}", "error")
            return
        ui.print_status(f"Selected: {vm.name} ({vm.zone})", "success")
        can_start, can_stop = get_start_stop_permissions(gcloud, vm, fav_project_id, cache, use_cache)
        action = ui.select_action(is_favorite=True, can_start=can_start, can_stop=can_stop)
        handle_action(action, gcloud, vm, fav_project_id, config, history)
        return

    # Select or use provided project
    if args.project:
        project_id = args.project
        ui.print_status(f"Using project: {project_id}", "info")
    elif config.default_project:
        project_id = config.default_project
        ui.print_status(f"Using default project: {project_id}", "info")
    else:
        projects = get_projects(gcloud, cache, use_cache)
        current = gcloud.get_current_project()

        selected = None
        while True:
            selected, mark_default = ui.select_project(projects, current, config.default_project)
            if not selected:
                ui.print_status("No project selected. Exiting.", "info")
                return
            if mark_default:
                config.default_project = selected.project_id
                config.save()
                ui.print_status(f"'{selected.project_id}' marked as default project", "success")
                continue
            break

        project_id = selected.project_id
    
    # Get VMs
    vms = get_vms(gcloud, project_id, config, cache, use_cache)
    
    # List mode
    if args.list:
        if not vms:
            ui.print_status(f"No VMs in project {project_id}", "info")
            return
        
        ui.print_section(f"VMs in {project_id}")
        header = f"{'Status':<8} {'Name':<30} {'Zone':<25} {'Type':<15} {'Internal IP'}"
        print(f"{ui.Colors.DIM}{header}{ui.Colors.RESET}")
        print(f"{ui.Colors.DIM}{'─' * 90}{ui.Colors.RESET}")
        
        for vm in vms:
            ip = vm.internal_ip or "N/A"
            print(f"{vm.status_icon:<8} {vm.name:<30} {vm.zone:<25} {vm.machine_type:<15} {ip}")
        return
    
    # Select or use provided VM
    if args.vm:
        # Find VM by name (and optionally zone)
        matching = [v for v in vms if v.name == args.vm]
        if args.zone:
            matching = [v for v in matching if v.zone == args.zone]
        
        if not matching:
            ui.print_status(f"VM '{args.vm}' not found in project '{project_id}'", "error")
            return
        elif len(matching) > 1:
            ui.print_status(f"Multiple VMs named '{args.vm}' found. Specify --zone", "error")
            for vm in matching:
                print(f"  - {vm.name} in {vm.zone}")
            return
        
        vm = matching[0]
    else:
        vm = ui.select_vm(vms, project_id, favorite_keys=set(config.favorites))
        if not vm:
            ui.print_status("No VM selected. Exiting.", "info")
            return
    
    ui.print_status(f"Selected: {vm.name} ({vm.zone})", "success")
    
    # Handle specific actions from CLI args
    if args.scp_up:
        handle_scp(gcloud, vm, project_id, args.scp_up, upload=True)
        return
    elif args.scp_down:
        handle_scp(gcloud, vm, project_id, args.scp_down, upload=False)
        return
    elif args.port_forward:
        handle_port_forward(gcloud, vm, project_id, args.port_forward)
        return
    
    # Show action menu
    can_start, can_stop = get_start_stop_permissions(gcloud, vm, project_id, cache, use_cache)
    action = ui.select_action(
        is_favorite=config.is_favorite(project_id, vm.zone, vm.name),
        can_start=can_start,
        can_stop=can_stop,
    )
    handle_action(action, gcloud, vm, project_id, config, history)


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    setup_logging(args.verbose, args.debug)
    
    # Load configuration
    config = Config.load()
    cache = Cache(ttl=config.cache_ttl)
    history = History(max_entries=config.max_history)
    
    # Handle configuration commands
    if args.clear_cache:
        cache.invalidate()
        ui.print_status("Cache cleared", "success")
        return
    
    if args.clear_history:
        history.clear()
        ui.print_status("History cleared", "success")
        return
    
    if args.config:
        config.save()  # Create default config file if it doesn't exist yet
        handle_config_menu(config)
        return
    
    # Initialize gcloud
    try:
        gcloud = GCloud()
    except GCloudNotFoundError as e:
        ui.print_status(str(e), "error")
        sys.exit(1)
    except GCloudAuthError as e:
        ui.print_status(str(e), "error")
        sys.exit(1)
    
    ui.print_header()
    
    # Show current account
    current_account = gcloud.get_active_account()
    if current_account:
        print(f"{ui.Colors.DIM}  Account: {current_account}{ui.Colors.RESET}\n")
    
    # Handle --accounts flag (list accounts)
    if args.accounts:
        ui.print_status("Fetching accounts...", "loading")
        accounts = gcloud.list_accounts()
        
        ui.print_section("Authenticated Accounts")
        for acc in accounts:
            prefix = "★ " if acc.is_active else "  "
            status = f"{ui.Colors.GREEN}(active){ui.Colors.RESET}" if acc.is_active else ""
            print(f"  {prefix}{acc.email} {status}")
        print()
        return
    
    try:
        interactive_mode(gcloud, config, cache, history, args)
    except GCloudError as e:
        ui.print_status(str(e), "error")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{ui.Colors.DIM}Cancelled.{ui.Colors.RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
