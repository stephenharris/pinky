import json
from pathlib import Path

class Config:
    _instance = None

    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load(config_path)
        return cls._instance

    def _load(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parents[2] / "config.json"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as f:
            self._data = json.load(f)

    def get(self, *keys, default=None):
        """Access nested keys with multiple arguments."""
        data = self._data
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, default)
            else:
                return default
        return data

