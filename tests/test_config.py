"""Tests for gcloud_selector.config module."""

import json
import pytest
from pathlib import Path

from gcloud_selector.config import Config, History, Cache, HistoryEntry


class TestConfig:
    """Tests for Config class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.default_project is None
        assert config.favorites == []
        assert config.max_history == 50
        assert config.cache_ttl == 300
        assert config.cache_enabled is True
        assert config.ssh_extra_args == ""
        assert config.zone_filter == ""
        assert config.show_stopped_vms is True
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = Config(
            default_project="my-project",
            cache_ttl=600,
            show_stopped_vms=False
        )
        
        assert config.default_project == "my-project"
        assert config.cache_ttl == 600
        assert config.show_stopped_vms is False
    
    def test_save_and_load(self, tmp_path, monkeypatch):
        """Test saving and loading configuration."""
        # Patch config directory
        import gcloud_selector.config as cfg
        monkeypatch.setattr(cfg, 'CONFIG_DIR', tmp_path)
        monkeypatch.setattr(cfg, 'CONFIG_FILE', tmp_path / 'config.json')
        
        # Create and save config
        config = Config(default_project="test-project", cache_ttl=600)
        config.save()
        
        # Load and verify
        loaded = Config.load()
        assert loaded.default_project == "test-project"
        assert loaded.cache_ttl == 600


class TestHistory:
    """Tests for History class."""
    
    def test_add_entry(self, tmp_path, monkeypatch):
        """Test adding history entries."""
        import gcloud_selector.config as cfg
        monkeypatch.setattr(cfg, 'CONFIG_DIR', tmp_path)
        monkeypatch.setattr(cfg, 'HISTORY_FILE', tmp_path / 'history.json')
        
        history = History(max_entries=10)
        history.add("project-1", "zone-a", "vm-1")
        
        recent = history.get_recent(10)
        assert len(recent) == 1
        assert recent[0].vm_name == "vm-1"
    
    def test_max_entries(self, tmp_path, monkeypatch):
        """Test history respects max entries."""
        import gcloud_selector.config as cfg
        monkeypatch.setattr(cfg, 'CONFIG_DIR', tmp_path)
        monkeypatch.setattr(cfg, 'HISTORY_FILE', tmp_path / 'history.json')
        
        history = History(max_entries=3)
        
        for i in range(5):
            history.add(f"project-{i}", "zone", f"vm-{i}")
        
        recent = history.get_recent(10)
        assert len(recent) == 3
        # Most recent should be first
        assert recent[0].vm_name == "vm-4"
    
    def test_clear(self, tmp_path, monkeypatch):
        """Test clearing history."""
        import gcloud_selector.config as cfg
        monkeypatch.setattr(cfg, 'CONFIG_DIR', tmp_path)
        monkeypatch.setattr(cfg, 'HISTORY_FILE', tmp_path / 'history.json')
        
        history = History()
        history.add("project", "zone", "vm")
        history.clear()
        
        assert len(history.get_recent(10)) == 0


class TestCache:
    """Tests for Cache class."""
    
    def test_set_and_get(self, tmp_path, monkeypatch):
        """Test setting and getting cache values."""
        import gcloud_selector.config as cfg
        monkeypatch.setattr(cfg, 'CONFIG_DIR', tmp_path)
        monkeypatch.setattr(cfg, 'CACHE_FILE', tmp_path / 'cache.json')
        
        cache = Cache(ttl=300)
        cache.set("key", {"data": "value"})
        
        result = cache.get("key")
        assert result == {"data": "value"}
    
    def test_expiration(self, tmp_path, monkeypatch):
        """Test cache expiration."""
        import time
        import gcloud_selector.config as cfg
        monkeypatch.setattr(cfg, 'CONFIG_DIR', tmp_path)
        monkeypatch.setattr(cfg, 'CACHE_FILE', tmp_path / 'cache.json')
        
        cache = Cache(ttl=1)  # 1 second TTL
        cache.set("key", "value")
        
        # Should exist immediately
        assert cache.get("key") == "value"
        
        # Should expire after TTL
        time.sleep(1.1)
        assert cache.get("key") is None
    
    def test_invalidate(self, tmp_path, monkeypatch):
        """Test cache invalidation."""
        import gcloud_selector.config as cfg
        monkeypatch.setattr(cfg, 'CONFIG_DIR', tmp_path)
        monkeypatch.setattr(cfg, 'CACHE_FILE', tmp_path / 'cache.json')
        
        cache = Cache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        # Invalidate single key
        cache.invalidate("key1")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        
        # Invalidate all
        cache.invalidate()
        assert cache.get("key2") is None
