"""
Settings Manager - Persistent storage for user preferences
"""

import json
from pathlib import Path
from typing import Any


class SettingsManager:
    """Manages saving/loading application settings to JSON."""

    def __init__(self, settings_file: str = "restoration_settings.json"):
        """
        Initialize settings manager.

        Args:
            settings_file: Path to settings JSON file (relative to CWD)
        """
        self.settings_file = Path(settings_file)
        self._settings = {}

    def load_settings(self) -> dict[str, Any]:
        """
        Load settings from JSON file.

        Returns:
            Dictionary of settings, empty dict if file doesn't exist
        """
        if not self.settings_file.exists():
            return {}

        try:
            with open(self.settings_file, encoding="utf-8") as f:
                self._settings = json.load(f)
            return self._settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}

    def save_settings(self, settings: dict[str, Any]) -> bool:
        """
        Save settings to JSON file.

        Args:
            settings: Dictionary of settings to save

        Returns:
            True if successful, False otherwise
        """
        try:
            self._settings = settings
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set a setting value (must call save_settings to persist)."""
        self._settings[key] = value

    def save(self, key: str, value: Any) -> bool:
        """
        Set a setting value and immediately persist to disk.

        Args:
            key: Setting key
            value: Setting value

        Returns:
            True if successful, False otherwise
        """
        self._settings[key] = value
        return self.save_settings(self._settings)


class PresetManager:
    """Manages user-created restoration presets."""

    def __init__(self, presets_file: str = "restoration_presets.json"):
        """
        Initialize preset manager.

        Args:
            presets_file: Path to presets JSON file
        """
        self.presets_file = Path(presets_file)
        self._presets = {}

    def load_presets(self) -> dict[str, dict[str, Any]]:
        """
        Load presets from JSON file.

        Returns:
            Dictionary of {preset_name: settings_dict}
        """
        if not self.presets_file.exists():
            return {}

        try:
            with open(self.presets_file, encoding="utf-8") as f:
                self._presets = json.load(f)
            return self._presets
        except Exception as e:
            print(f"Error loading presets: {e}")
            return {}

    def save_presets(self) -> bool:
        """Save presets to JSON file."""
        try:
            with open(self.presets_file, "w", encoding="utf-8") as f:
                json.dump(self._presets, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving presets: {e}")
            return False

    def add_preset(self, name: str, settings: dict[str, Any]) -> bool:
        """Add or update a preset."""
        self._presets[name] = settings
        return self.save_presets()

    def delete_preset(self, name: str) -> bool:
        """Delete a preset."""
        if name in self._presets:
            del self._presets[name]
            return self.save_presets()
        return False

    def get_preset(self, name: str) -> dict[str, Any]:
        """Get preset settings by name."""
        return self._presets.get(name, {})

    def get_preset_names(self) -> list:
        """Get list of all preset names."""
        return list(self._presets.keys())
