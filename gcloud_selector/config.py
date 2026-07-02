"""Configuration management for GCloud Selector."""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Default config directory
CONFIG_DIR = Path.home() / ".config" / "gcloud-selector"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_FILE = CONFIG_DIR / "cache.json"
HISTORY_FILE = CONFIG_DIR / "history.json"


@dataclass
class Config:
    """Application configuration."""
    # Default project to use (skip project selection if set)
    default_project: Optional[str] = None
    
    # Favorite VMs for quick access (list of "project:zone:vm" strings)
    favorites: list[str] = field(default_factory=list)
    
    # Maximum history entries to keep
    max_history: int = 50
    
    # Cache TTL in seconds (default: 5 minutes)
    cache_ttl: int = 300
    
    # Enable caching
    cache_enabled: bool = True
    
    # SSH options
    ssh_extra_args: str = ""
    
    # Default zone filter (empty = all zones)
    zone_filter: str = ""
    
    # Show stopped VMs
    show_stopped_vms: bool = True
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    return cls(**data)
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
        return cls()
    
    def save(self):
        """Save configuration to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)
        logger.debug(f"Config saved to {CONFIG_FILE}")

    def is_favorite(self, project: str, zone: str, vm_name: str) -> bool:
        """Check whether a VM is favorited."""
        return f"{project}:{zone}:{vm_name}" in self.favorites

    def add_favorite(self, project: str, zone: str, vm_name: str) -> None:
        """Add a VM to favorites and persist the change."""
        key = f"{project}:{zone}:{vm_name}"
        if key not in self.favorites:
            self.favorites.append(key)
            self.save()

    def remove_favorite(self, project: str, zone: str, vm_name: str) -> None:
        """Remove a VM from favorites and persist the change."""
        key = f"{project}:{zone}:{vm_name}"
        if key in self.favorites:
            self.favorites.remove(key)
            self.save()


@dataclass
class HistoryEntry:
    """A connection history entry."""
    project: str
    zone: str
    vm_name: str
    timestamp: str
    
    def to_key(self) -> str:
        """Return unique key for this entry."""
        return f"{self.project}:{self.zone}:{self.vm_name}"


class History:
    """Manages connection history."""
    
    def __init__(self, max_entries: int = 50):
        self.max_entries = max_entries
        self.entries: list[HistoryEntry] = []
        self._load()
    
    def _load(self):
        """Load history from file."""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r") as f:
                    data = json.load(f)
                    self.entries = [HistoryEntry(**e) for e in data]
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Error loading history: {e}")
                self.entries = []
    
    def _save(self):
        """Save history to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w") as f:
            json.dump([asdict(e) for e in self.entries], f, indent=2)
    
    def add(self, project: str, zone: str, vm_name: str):
        """Add a new history entry."""
        from datetime import datetime
        
        entry = HistoryEntry(
            project=project,
            zone=zone,
            vm_name=vm_name,
            timestamp=datetime.now().isoformat()
        )
        
        # Remove existing entry for same VM (to move it to top)
        self.entries = [e for e in self.entries if e.to_key() != entry.to_key()]
        
        # Add to front
        self.entries.insert(0, entry)
        
        # Trim to max entries
        self.entries = self.entries[:self.max_entries]
        
        self._save()
    
    def get_recent(self, limit: int = 10) -> list[HistoryEntry]:
        """Get most recent entries."""
        return self.entries[:limit]
    
    def clear(self):
        """Clear all history."""
        self.entries = []
        self._save()


class Cache:
    """Simple cache for API responses."""
    
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._cache: dict = {}
        self._load()
    
    def _load(self):
        """Load cache from file."""
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r") as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, TypeError):
                self._cache = {}
    
    def _save(self):
        """Save cache to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(self._cache, f)
    
    def get(self, key: str) -> Optional[any]:
        """Get cached value if not expired."""
        import time
        
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry.get("timestamp", 0) < self.ttl:
                logger.debug(f"Cache hit for {key}")
                return entry.get("data")
            else:
                logger.debug(f"Cache expired for {key}")
        return None
    
    def set(self, key: str, data: any):
        """Set cache value."""
        import time
        
        self._cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
        self._save()
        logger.debug(f"Cached {key}")
    
    def invalidate(self, key: Optional[str] = None):
        """Invalidate cache entry or all cache."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache = {}
        self._save()
