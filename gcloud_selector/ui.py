"""Terminal UI components for GCloud Selector."""

import sys
from typing import Optional, Callable
from simple_term_menu import TerminalMenu

from .gcloud import Project, VM, Account
from .config import Config, HistoryEntry


# ANSI color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BG_CYAN = "\033[46m"
    BG_BLUE = "\033[44m"


def print_header():
    """Print application header."""
    print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║  {Colors.BOLD}🌩️  GCloud VM Selector{Colors.RESET}{Colors.CYAN}                                       ║
║  {Colors.DIM}Connect to GCP VMs via IAP Tunnel{Colors.RESET}{Colors.CYAN}                            ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
""")


def print_status(message: str, status: str = "info"):
    """Print a status message."""
    icons = {
        "info": f"{Colors.BLUE}ℹ️ ",
        "success": f"{Colors.GREEN}✅",
        "error": f"{Colors.RED}❌",
        "warning": f"{Colors.YELLOW}⚠️ ",
        "loading": f"{Colors.CYAN}⏳",
    }
    icon = icons.get(status, icons["info"])
    print(f"{icon} {message}{Colors.RESET}")


def print_section(title: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'─' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}\n")


def confirm(message: str, default: bool = False) -> bool:
    """Ask for confirmation."""
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = input(f"{Colors.YELLOW}? {message}{suffix}{Colors.RESET}").strip().lower()
    
    if not response:
        return default
    return response in ("y", "yes")


def create_menu(items: list[str], title: str = "",
                multi_select: bool = False,
                preview_command: Optional[Callable] = None,
                search_key: Optional[str] = "/",
                accept_keys: tuple[str, ...] = ("enter",),
                status_bar: str = "Press / to search, q to quit") -> TerminalMenu:
    """Create a styled terminal menu."""
    return TerminalMenu(
        items,
        title=title,
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("bg_cyan", "fg_black", "bold"),
        search_key=search_key,
        search_highlight_style=("fg_yellow", "bold"),
        multi_select=multi_select,
        show_multi_select_hint=multi_select,
        preview_command=preview_command,
        preview_size=0.3,
        accept_keys=accept_keys,
        cycle_cursor=True,
        clear_screen=False,
        status_bar=status_bar,
        status_bar_style=("fg_black", "bg_gray"),
    )


def select_account(accounts: list[Account], 
                   current_account: Optional[str] = None) -> Optional[Account]:
    """Display account selection menu."""
    if not accounts:
        print_status("No accounts found. Run 'gcloud auth login' first.", "error")
        return None
    
    # Create menu items
    items = []
    for acc in accounts:
        prefix = "★ " if acc.email == current_account else "  "
        items.append(f"{prefix}{acc.email}")
    
    print(f"\n{Colors.DIM}Use ↑/↓ to navigate, / to search, Enter to select, q to quit{Colors.RESET}\n")
    
    menu = create_menu(items, title="👤 Select Account:")
    index = menu.show()
    
    if index is None:
        return None
    
    return accounts[index]


def select_project(projects: list[Project],
                   current_project: Optional[str] = None,
                   default_project: Optional[str] = None) -> tuple[Optional[Project], bool]:
    """Display project selection menu.

    Returns (project, mark_as_default). mark_as_default is True when the user
    pressed 'd' on the highlighted project instead of Enter, requesting it be
    set as the config default. Returns (None, False) if the menu was cancelled.
    """
    if not projects:
        print_status("No projects found.", "error")
        return None, False

    # Create menu items
    items = []
    for p in projects:
        prefix = "★ " if p.project_id == current_project else "  "
        suffix = "  (default)" if p.project_id == default_project else ""
        items.append(f"{prefix}{p.name} ({p.project_id}){suffix}")

    print(f"\n{Colors.DIM}Use ↑/↓ to navigate, / to search, Enter to select, "
          f"d to mark as default, q to quit{Colors.RESET}\n")

    menu = create_menu(
        items,
        title="📁 Select Project:",
        accept_keys=("enter", "d"),
        status_bar="Press / to search, d to mark default, q to quit",
    )
    index = menu.show()

    if index is None:
        return None, False

    return projects[index], menu.chosen_accept_key == "d"


# Menu entries fed to TerminalMenu must stick to single-width, unambiguous
# glyphs (no full-width/emoji-presentation characters). Terminals differ on
# how wide they actually render emoji, and when that disagrees with the
# width TerminalMenu computed, its incremental redraw miscounts lines and
# leaves stale copies of entries behind when navigating up/down.
_STATUS_MARKERS = {
    "RUNNING": "●",
    "TERMINATED": "○",
    "STOPPED": "○",
    "SUSPENDED": "◐",
    "STAGING": "◐",
    "PROVISIONING": "◐",
    "STOPPING": "◑",
    "SUSPENDING": "◑",
}


def _menu_status_marker(status: str) -> str:
    """Return a single-width status marker safe to use inside a TerminalMenu entry."""
    return _STATUS_MARKERS.get(status, "◌")


def select_vm(vms: list[VM], project_id: str,
             favorite_keys: Optional[set[str]] = None) -> Optional[VM]:
    """Display VM selection menu."""
    if not vms:
        print_status(f"No VMs found in project '{project_id}'.", "warning")
        return None

    favorite_keys = favorite_keys or set()

    # Create menu items with details
    items = []
    for vm in vms:
        internal_ip = vm.internal_ip or "No IP"
        external_ip = vm.external_ip or "No external IP"
        marker = _menu_status_marker(vm.status)
        star = "★" if f"{project_id}:{vm.zone}:{vm.name}" in favorite_keys else " "
        items.append(
            f"{marker} {star} {vm.name:<30} {vm.zone:<25} {internal_ip:<15} {external_ip}"
        )

    print(f"\n{Colors.DIM}Use ↑/↓ to navigate, / to search, Enter to select, q to quit{Colors.RESET}\n")

    # Header for columns
    header = f"     {'Name':<30} {'Zone':<25} {'Internal IP':<15} {'External IP'}"
    print(f"{Colors.DIM}{header}{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * 80}{Colors.RESET}")

    menu = create_menu(items, title="💻 Select VM:")
    index = menu.show()

    if index is None:
        return None

    return vms[index]


def select_action(is_favorite: bool = False, can_start: bool = True,
                  can_stop: bool = True) -> Optional[str]:
    """Display action selection menu."""
    favorite_action = (
        ("unfavorite", "★ Remove from Favorites")
        if is_favorite
        else ("favorite", "☆ Add to Favorites")
    )
    actions = [
        ("ssh", "SSH Connect"),
        ("scp_upload", "SCP Upload"),
        ("scp_download", "SCP Download"),
        ("port_forward", "Port Forward"),
    ]
    if can_start:
        actions.append(("start", "Start VM"))
    if can_stop:
        actions.append(("stop", "Stop VM"))
    actions.append(favorite_action)
    actions.append(("info", "VM Info"))

    items = [label for _, label in actions]

    menu = create_menu(items, title="Select Action:")
    index = menu.show()

    if index is None:
        return None

    return actions[index][0]


def select_from_favorites(favorites: list[str]) -> Optional[tuple[str, str, str]]:
    """Display favorite VM selection menu. Returns (project, zone, vm_name) or None."""
    if not favorites:
        print_status("No favorite VMs yet. Add one from a VM's action menu.", "info")
        return None

    parsed = [tuple(fav.split(":", 2)) for fav in favorites if fav.count(":") == 2]
    if not parsed:
        print_status("No valid favorite VMs found.", "info")
        return None

    items = [
        f"★ {vm_name:<30} {project:<25} {zone}"
        for project, zone, vm_name in parsed
    ]

    menu = create_menu(items, title="Favorite VMs:")
    index = menu.show()

    if index is None:
        return None

    return parsed[index]


def select_config_menu(config: Config) -> Optional[str]:
    """Display the configuration menu. Returns the selected setting's key, or None."""
    fields = [
        ("default_project", "Default project", config.default_project or "(none — always prompt)"),
        ("cache_enabled", "Caching enabled", str(config.cache_enabled)),
        ("cache_ttl", "Cache TTL (seconds)", str(config.cache_ttl)),
        ("zone_filter", "Zone filter", config.zone_filter or "(all zones)"),
        ("show_stopped_vms", "Show stopped VMs", str(config.show_stopped_vms)),
        ("ssh_extra_args", "Extra SSH arguments", config.ssh_extra_args or "(none)"),
        ("max_history", "Max history entries", str(config.max_history)),
        ("favorites", "Manage favorites", f"{len(config.favorites)} saved"),
    ]

    items = [f"{label:<22} {value}" for _, label, value in fields]

    menu = create_menu(items, title="Configuration (Enter to edit, q to exit):")
    index = menu.show()

    if index is None:
        return None

    return fields[index][0]


def select_from_history(history: list[HistoryEntry]) -> Optional[HistoryEntry]:
    """Display history selection menu."""
    if not history:
        print_status("No connection history.", "info")
        return None
    
    items = []
    for entry in history:
        items.append(f"  {entry.vm_name} ({entry.project}) - {entry.zone}")
    
    menu = create_menu(items, title="📜 Recent Connections:")
    index = menu.show()
    
    if index is None:
        return None
    
    return history[index]


def get_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default."""
    default_hint = f" [{default}]" if default else ""
    value = input(f"{Colors.CYAN}? {prompt}{default_hint}: {Colors.RESET}").strip()
    return value if value else default


def get_port(prompt: str, default: int = 0) -> Optional[int]:
    """Get port number from user."""
    default_hint = f" [{default}]" if default else ""
    value = input(f"{Colors.CYAN}? {prompt}{default_hint}: {Colors.RESET}").strip()
    
    if not value and default:
        return default
    
    try:
        port = int(value)
        if 1 <= port <= 65535:
            return port
        print_status("Port must be between 1 and 65535", "error")
        return None
    except ValueError:
        print_status("Invalid port number", "error")
        return None


def display_vm_info(vm: VM, project_id: str):
    """Display detailed VM information."""
    print_section(f"VM Information: {vm.name}")
    
    info = [
        ("Project", project_id),
        ("Name", vm.name),
        ("Zone", vm.zone),
        ("Status", f"{vm.status_icon} {vm.status}"),
        ("Machine Type", vm.machine_type),
        ("Internal IP", vm.internal_ip or "N/A"),
        ("External IP", vm.external_ip or "N/A"),
    ]
    
    for label, value in info:
        print(f"  {Colors.DIM}{label:15}{Colors.RESET} {value}")
    
    print()
