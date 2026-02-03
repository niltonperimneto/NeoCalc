import json
import os
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    _instance = None
    _config = {}
    _config_path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _get_config_dir(self):
        """Returns path to user config directory."""
        # Simple implementation using XDG_CONFIG_HOME or ~/.config
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        p = os.path.join(xdg_config, "neocalc")
        if not os.path.exists(p):
            try:
                os.makedirs(p)
            except OSError:
                pass
        return p

    def _load_config(self):
        self._config_path = os.path.join(self._get_config_dir(), "config.json")
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r') as f:
                    self._config = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self._config = {}
        else:
            self._config = {}

    def save(self):
        if self._config_path:
            try:
                with open(self._config_path, 'w') as f:
                    json.dump(self._config, f, indent=4)
            except Exception as e:
                logger.error(f"Failed to save config: {e}")

    def get(self, key, default=None):
        return self._config.get(key, default)

    def set(self, key, value):
        self._config[key] = value
        self.save()
