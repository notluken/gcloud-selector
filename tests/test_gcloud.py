"""Tests for gcloud_selector.gcloud module."""

import pytest
from gcloud_selector.gcloud import Project, VM


class TestProject:
    """Tests for Project class."""
    
    def test_from_dict(self):
        """Test creating Project from dict."""
        data = {
            "projectId": "my-project-123",
            "name": "My Project",
            "projectNumber": "123456789",
            "lifecycleState": "ACTIVE"
        }
        
        project = Project.from_dict(data)
        
        assert project.project_id == "my-project-123"
        assert project.name == "My Project"
        assert project.project_number == "123456789"
        assert project.state == "ACTIVE"
    
    def test_str(self):
        """Test string representation."""
        project = Project(
            project_id="my-project",
            name="My Project",
            project_number="123",
            state="ACTIVE"
        )
        
        assert str(project) == "My Project (my-project)"


class TestVM:
    """Tests for VM class."""
    
    def test_from_dict(self):
        """Test creating VM from dict."""
        data = {
            "name": "web-server",
            "zone": "https://compute.googleapis.com/zones/us-central1-a",
            "status": "RUNNING",
            "machineType": "https://compute.googleapis.com/machineTypes/e2-medium",
            "networkInterfaces": [
                {
                    "networkIP": "10.128.0.2",
                    "accessConfigs": [{"natIP": "34.123.45.67"}]
                }
            ]
        }
        
        vm = VM.from_dict(data)
        
        assert vm.name == "web-server"
        assert vm.zone == "us-central1-a"
        assert vm.status == "RUNNING"
        assert vm.machine_type == "e2-medium"
        assert vm.internal_ip == "10.128.0.2"
        assert vm.external_ip == "34.123.45.67"
    
    def test_is_running(self):
        """Test is_running property."""
        running_vm = VM("vm1", "zone", "RUNNING", "e2-medium", None, None)
        stopped_vm = VM("vm2", "zone", "STOPPED", "e2-medium", None, None)
        
        assert running_vm.is_running is True
        assert stopped_vm.is_running is False
    
    def test_status_icon(self):
        """Test status icons."""
        test_cases = [
            ("RUNNING", "🟢"),
            ("STOPPED", "🔴"),
            ("TERMINATED", "🔴"),
            ("SUSPENDED", "🟡"),
            ("STAGING", "🟡"),
            ("STOPPING", "🟠"),
            ("UNKNOWN", "⚪"),
        ]
        
        for status, expected_icon in test_cases:
            vm = VM("test", "zone", status, "type", None, None)
            assert vm.status_icon == expected_icon, f"Failed for status {status}"
