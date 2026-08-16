import os
import json

DEFAULT_CONFIG = {
    "sound_enabled": True,
    "double_tap_timeout": 0.42,
    "size_normal": 32,
    "size_large": 64,
    "size_xl": 96,
    "sizes_cycle": [32, 64, 96],
    "last_color": "red",
    "enable_mouse_sonar": True
}

class Config:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        self.config_path = config_path
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
