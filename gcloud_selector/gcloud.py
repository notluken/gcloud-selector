"""GCloud API interactions."""

import subprocess
import json
import logging
import urllib.error
import urllib.request
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class GCloudError(Exception):
    """Exception raised for gcloud command errors."""
    pass


class GCloudNotFoundError(GCloudError):
    """Exception raised when gcloud CLI is not installed."""
    pass


class GCloudAuthError(GCloudError):
    """Exception raised for authentication issues."""
    pass


@dataclass
class Account:
    """Represents a GCP account."""
    email: str
    is_active: bool
    
    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        return cls(
            email=data.get("account", ""),
            is_active=data.get("status", "") == "ACTIVE"
        )
    
    def __str__(self) -> str:
        prefix = "★ " if self.is_active else "  "
        return f"{prefix}{self.email}"


@dataclass
class Project:
    """Represents a GCP project."""
    project_id: str
    name: str
    project_number: str
    state: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        return cls(
            project_id=data.get("projectId", ""),
            name=data.get("name", ""),
            project_number=data.get("projectNumber", ""),
            state=data.get("lifecycleState", "ACTIVE")
        )
    
    def __str__(self) -> str:
        return f"{self.name} ({self.project_id})"


@dataclass
class VM:
    """Represents a GCP VM instance."""
    name: str
    zone: str
    status: str
    machine_type: str
    internal_ip: Optional[str]
    external_ip: Optional[str]
    
    @classmethod
    def from_dict(cls, data: dict) -> "VM":
        # Extract zone name from full URL
        zone_full = data.get("zone", "")
        zone = zone_full.split("/")[-1] if zone_full else ""
        
        # Extract machine type name
        machine_type_full = data.get("machineType", "")
        machine_type = machine_type_full.split("/")[-1] if machine_type_full else ""
        
        # Extract IPs
        internal_ip = None
        external_ip = None
        network_interfaces = data.get("networkInterfaces", [])
        if network_interfaces:
            internal_ip = network_interfaces[0].get("networkIP")
            access_configs = network_interfaces[0].get("accessConfigs", [])
            if access_configs:
                external_ip = access_configs[0].get("natIP")
        
        return cls(
            name=data.get("name", ""),
            zone=zone,
            status=data.get("status", "UNKNOWN"),
            machine_type=machine_type,
            internal_ip=internal_ip,
            external_ip=external_ip
        )
    
    @property
    def is_running(self) -> bool:
        return self.status == "RUNNING"
    
    @property
    def status_icon(self) -> str:
        icons = {
            "RUNNING": "🟢",
            "TERMINATED": "🔴",
            "STOPPED": "🔴",
            "SUSPENDED": "🟡",
            "STAGING": "🟡",
            "PROVISIONING": "🟡",
            "STOPPING": "🟠",
            "SUSPENDING": "🟠",
        }
        return icons.get(self.status, "⚪")
    
    def __str__(self) -> str:
        return f"{self.status_icon} {self.name} ({self.zone}) - {self.machine_type}"


class GCloud:
    """Wrapper for gcloud CLI commands."""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
        self._verify_installation()
    
    def _verify_installation(self):
        """Verify gcloud is installed and authenticated."""
        try:
            result = subprocess.run(
                ["gcloud", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise GCloudNotFoundError("gcloud CLI returned an error")
        except FileNotFoundError:
            raise GCloudNotFoundError(
                "gcloud CLI not found. Please install the Google Cloud SDK: "
                "https://cloud.google.com/sdk/docs/install"
            )
    
    def _run(self, args: list[str], timeout: Optional[int] = None) -> str:
        """Run a gcloud command and return output."""
        timeout = timeout or self.timeout
        cmd = ["gcloud"] + args
        
        logger.debug(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                
                # Check for common errors
                if "not authenticated" in error_msg.lower() or "login" in error_msg.lower():
                    raise GCloudAuthError(
                        "Not authenticated. Run 'gcloud auth login' first."
                    )
                
                raise GCloudError(f"gcloud error: {error_msg}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise GCloudError(f"Command timed out after {timeout} seconds")
    
    def list_projects(self) -> list[Project]:
        """List all accessible projects."""
        output = self._run([
            "projects", "list",
            "--format=json",
            "--filter=lifecycleState:ACTIVE"
        ])
        
        try:
            data = json.loads(output) if output else []
            return [Project.from_dict(p) for p in data]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse projects: {e}")
            raise GCloudError("Failed to parse project list")
    
    def list_vms(self, project_id: str, zone_filter: Optional[str] = None, 
                 include_stopped: bool = True) -> list[VM]:
        """List VMs in a project."""
        args = [
            "compute", "instances", "list",
            f"--project={project_id}",
            "--format=json"
        ]
        
        # Build filter
        filters = []
        if zone_filter:
            args.append(f"--zones={zone_filter}")
        if not include_stopped:
            filters.append("status=RUNNING")
        
        if filters:
            args.append(f"--filter={' AND '.join(filters)}")
        
        output = self._run(args)
        
        try:
            data = json.loads(output) if output else []
            return [VM.from_dict(v) for v in data]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse VMs: {e}")
            raise GCloudError("Failed to parse VM list")
    
    def get_current_project(self) -> Optional[str]:
        """Get the currently configured project."""
        try:
            output = self._run(["config", "get-value", "project"], timeout=10)
            return output if output and output != "(unset)" else None
        except GCloudError:
            return None
    
    def list_accounts(self) -> list[Account]:
        """List all authenticated accounts."""
        output = self._run([
            "auth", "list",
            "--format=json"
        ])
        
        try:
            data = json.loads(output) if output else []
            return [Account.from_dict(a) for a in data]
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse accounts: {e}")
            raise GCloudError("Failed to parse account list")
    
    def get_active_account(self) -> Optional[str]:
        """Get the currently active account."""
        try:
            output = self._run(["config", "get-value", "account"], timeout=10)
            return output if output and output != "(unset)" else None
        except GCloudError:
            return None
    
    def set_account(self, email: str) -> bool:
        """Switch to a different account."""
        try:
            self._run(["config", "set", "account", email], timeout=10)
            logger.info(f"Switched to account: {email}")
            return True
        except GCloudError as e:
            logger.error(f"Failed to switch account: {e}")
            return False
    
    def ssh_command(self, vm: VM, project_id: str, extra_args: str = "") -> list[str]:
        """Generate SSH command for a VM."""
        cmd = [
            "gcloud", "compute", "ssh",
            vm.name,
            f"--zone={vm.zone}",
            f"--project={project_id}",
            "--tunnel-through-iap"
        ]
        
        if extra_args:
            cmd.extend(extra_args.split())
        
        return cmd
    
    def scp_command(self, vm: VM, project_id: str, source: str, dest: str, 
                    to_remote: bool = True) -> list[str]:
        """Generate SCP command for a VM."""
        remote_path = f"{vm.name}:{dest}" if to_remote else f"{vm.name}:{source}"
        local_path = source if to_remote else dest
        
        cmd = [
            "gcloud", "compute", "scp",
            f"--zone={vm.zone}",
            f"--project={project_id}",
            "--tunnel-through-iap"
        ]
        
        if to_remote:
            cmd.extend([local_path, remote_path])
        else:
            cmd.extend([remote_path, local_path])
        
        return cmd
    
    def port_forward_command(self, vm: VM, project_id: str, 
                             local_port: int, remote_port: int) -> list[str]:
        """Generate port forwarding command for a VM."""
        return [
            "gcloud", "compute", "ssh",
            vm.name,
            f"--zone={vm.zone}",
            f"--project={project_id}",
            "--tunnel-through-iap",
            "--",
            "-N", "-L", f"{local_port}:localhost:{remote_port}"
        ]
    
    def start_vm(self, vm: VM, project_id: str) -> bool:
        """Start a stopped VM."""
        try:
            self._run([
                "compute", "instances", "start",
                vm.name,
                f"--zone={vm.zone}",
                f"--project={project_id}"
            ], timeout=120)
            return True
        except GCloudError as e:
            logger.error(f"Failed to start VM: {e}")
            return False
    
    def stop_vm(self, vm: VM, project_id: str) -> bool:
        """Stop a running VM."""
        try:
            self._run([
                "compute", "instances", "stop",
                vm.name,
                f"--zone={vm.zone}",
                f"--project={project_id}"
            ], timeout=120)
            return True
        except GCloudError as e:
            logger.error(f"Failed to stop VM: {e}")
            return False

    def test_permissions(self, vm: VM, project_id: str, permissions: list[str]) -> set[str]:
        """Return the subset of `permissions` the active credentials hold on this VM.

        Falls back to granting all requested permissions if the check itself
        fails (e.g. transient network issue), so a broken check never hides
        an action the user could actually perform.
        """
        try:
            token = self._run(["auth", "print-access-token"], timeout=10)
        except GCloudError as e:
            logger.warning(f"Could not fetch access token for permission check: {e}")
            return set(permissions)

        url = (
            f"https://compute.googleapis.com/compute/v1/projects/{project_id}"
            f"/zones/{vm.zone}/instances/{vm.name}/testIamPermissions"
        )
        request = urllib.request.Request(
            url,
            data=json.dumps({"permissions": permissions}).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read())
                return set(data.get("permissions", []))
        except (urllib.error.URLError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Permission check failed, assuming allowed: {e}")
            return set(permissions)
