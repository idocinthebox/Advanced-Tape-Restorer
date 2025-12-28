"""
Configuration Management for Advanced Tape Restorer
Handles user preferences for cache locations, performance settings, etc.
"""

import os
import json
from pathlib import Path
from typing import Optional


class CacheConfig:
    """
    Manages cache configuration with multiple priority levels:
    1. Environment variables (highest priority)
    2. User settings file
    3. Default values (lowest priority)

    Usage:
        config = CacheConfig()
        cache_dir = config.get_cache_dir()

        # Or set custom location
        config.set_cache_dir("/path/to/cache")
    """

    CONFIG_FILE = Path("tape_restorer_config.json")

    # Default settings
    DEFAULTS = {
        "cache_dir": "./cache",
        "cache_max_size_gb": 10.0,
        "cache_ttl_hours": 24,
        "checkpoint_dir": "./checkpoints",
    }

    def __init__(self):
        """Initialize config manager."""
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file or create defaults."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    # Merge with defaults (in case new settings were added)
                    return {**self.DEFAULTS, **config}
            except Exception as e:
                print(f"[WARNING] Failed to load config: {e}, using defaults")

        return self.DEFAULTS.copy()

    def _save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4)
            return True
        except Exception as e:
            print(f"[WARNING] Failed to save config: {e}")
            return False

    def get_cache_dir(self) -> Path:
        """
        Get cache directory with priority:
        1. Environment variable TAPE_RESTORER_CACHE_DIR
        2. User config file
        3. Default: ./cache

        Returns:
            Path object for cache directory
        """
        # Check environment variable first
        env_cache = os.getenv("TAPE_RESTORER_CACHE_DIR")
        if env_cache:
            return Path(env_cache)

        # Check config file
        cache_dir = self._config.get("cache_dir", self.DEFAULTS["cache_dir"])
        return Path(cache_dir)

    def set_cache_dir(self, cache_dir: str, silent: bool = False) -> bool:
        """
        Set custom cache directory and persist to config.

        Args:
            cache_dir: Path to cache directory (can be relative or absolute)
            silent: If True, don't print confirmation message

        Returns:
            True if saved successfully, False otherwise
        """
        self._config["cache_dir"] = str(cache_dir)
        success = self._save_config()

        if success and not silent:
            print(f"[OK] Cache directory set to: {cache_dir}")

        return success

    def get_cache_max_size_gb(self) -> float:
        """Get maximum cache size in GB."""
        return float(
            self._config.get("cache_max_size_gb", self.DEFAULTS["cache_max_size_gb"])
        )

    def set_cache_max_size_gb(self, size_gb: float) -> bool:
        """Set maximum cache size in GB."""
        self._config["cache_max_size_gb"] = float(size_gb)
        return self._save_config()

    def get_cache_ttl_hours(self) -> int:
        """Get cache time-to-live in hours."""
        return int(
            self._config.get("cache_ttl_hours", self.DEFAULTS["cache_ttl_hours"])
        )

    def set_cache_ttl_hours(self, hours: int) -> bool:
        """Set cache time-to-live in hours."""
        self._config["cache_ttl_hours"] = int(hours)
        return self._save_config()

    def get_checkpoint_dir(self) -> Path:
        """
        Get checkpoint directory for resumable processing.

        Returns:
            Path object for checkpoint directory
        """
        # Check environment variable first
        env_checkpoint = os.getenv("TAPE_RESTORER_CHECKPOINT_DIR")
        if env_checkpoint:
            return Path(env_checkpoint)

        checkpoint_dir = self._config.get(
            "checkpoint_dir", self.DEFAULTS["checkpoint_dir"]
        )
        return Path(checkpoint_dir)

    def set_checkpoint_dir(self, checkpoint_dir: str, silent: bool = False) -> bool:
        """
        Set custom checkpoint directory.

        Args:
            checkpoint_dir: Path to checkpoint directory
            silent: If True, don't print confirmation message

        Returns:
            True if saved successfully, False otherwise
        """
        self._config["checkpoint_dir"] = str(checkpoint_dir)
        success = self._save_config()

        if success and not silent:
            print(f"[OK] Checkpoint directory set to: {checkpoint_dir}")

        return success

    def get_all(self) -> dict:
        """Get all configuration settings."""
        return self._config.copy()

    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults."""
        self._config = self.DEFAULTS.copy()
        return self._save_config()

    def print_config(self):
        """Print current configuration."""
        print("\n=== Advanced Tape Restorer Configuration ===")
        print(f"Cache Directory: {self.get_cache_dir()}")
        print(f"Cache Max Size: {self.get_cache_max_size_gb():.1f} GB")
        print(f"Cache TTL: {self.get_cache_ttl_hours()} hours")
        print(f"Checkpoint Directory: {self.get_checkpoint_dir()}")

        # Show environment overrides
        if os.getenv("TAPE_RESTORER_CACHE_DIR"):
            print("\n[INFO] Cache dir overridden by environment variable")
        if os.getenv("TAPE_RESTORER_CHECKPOINT_DIR"):
            print("[INFO] Checkpoint dir overridden by environment variable")

        print(f"\nConfig file: {self.CONFIG_FILE.absolute()}")


# Global config instance (singleton pattern)
_global_config: Optional[CacheConfig] = None


def get_config() -> CacheConfig:
    """
    Get global configuration instance.

    Usage:
        from core.config import get_config
        config = get_config()
        cache_dir = config.get_cache_dir()
    """
    global _global_config
    if _global_config is None:
        _global_config = CacheConfig()
    return _global_config


# Convenience functions
def get_cache_dir() -> Path:
    """Get configured cache directory."""
    return get_config().get_cache_dir()


def set_cache_dir(cache_dir: str) -> bool:
    """Set cache directory."""
    return get_config().set_cache_dir(cache_dir)


def get_checkpoint_dir() -> Path:
    """Get configured checkpoint directory."""
    return get_config().get_checkpoint_dir()


def set_checkpoint_dir(checkpoint_dir: str) -> bool:
    """Set checkpoint directory."""
    return get_config().set_checkpoint_dir(checkpoint_dir)


# CLI interface for testing
if __name__ == "__main__":
    import sys

    config = CacheConfig()

    if len(sys.argv) == 1:
        # No arguments - show current config
        config.print_config()

    elif sys.argv[1] == "set-cache":
        # Set cache directory
        if len(sys.argv) < 3:
            print("Usage: python config.py set-cache <directory>")
            sys.exit(1)

        cache_dir = sys.argv[2]
        if not config.set_cache_dir(cache_dir):
            print("[ERROR] Failed to save config")

    elif sys.argv[1] == "set-checkpoint":
        # Set checkpoint directory
        if len(sys.argv) < 3:
            print("Usage: python config.py set-checkpoint <directory>")
            sys.exit(1)

        checkpoint_dir = sys.argv[2]
        if not config.set_checkpoint_dir(checkpoint_dir):
            print("[ERROR] Failed to save config")

    elif sys.argv[1] == "set-size":
        # Set max cache size
        if len(sys.argv) < 3:
            print("Usage: python config.py set-size <size_in_gb>")
            sys.exit(1)

        try:
            size_gb = float(sys.argv[2])
            if config.set_cache_max_size_gb(size_gb):
                print(f"[OK] Cache max size set to: {size_gb} GB")
            else:
                print("[ERROR] Failed to save config")
        except ValueError:
            print("[ERROR] Size must be a number")

    elif sys.argv[1] == "reset":
        # Reset to defaults
        if config.reset_to_defaults():
            print("[OK] Configuration reset to defaults")
            config.print_config()
        else:
            print("[ERROR] Failed to reset config")

    else:
        print("Advanced Tape Restorer - Configuration Manager")
        print("\nUsage:")
        print("  python config.py                    Show current configuration")
        print("  python config.py set-cache <dir>    Set cache directory")
        print("  python config.py set-checkpoint <dir>  Set checkpoint directory")
        print("  python config.py set-size <gb>      Set max cache size in GB")
        print("  python config.py reset              Reset to defaults")
        print("\nEnvironment variables:")
        print("  TAPE_RESTORER_CACHE_DIR      Override cache directory")
        print("  TAPE_RESTORER_CHECKPOINT_DIR Override checkpoint directory")
