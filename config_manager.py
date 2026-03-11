import json

class ConfigManager:
    def __init__(self, filename="config.json", log=None):
        self.filename = filename
        self.log = log
        self._config = {}
        if self.log:
            self.log.info(f"[ConfigManager] Initializing, loading {self.filename}")
        try:
            with open(self.filename, "r") as f:
                self._config = json.load(f)
            if self.log:
                self.log.info(f"[ConfigManager] Loaded config: {self._config}")
        except Exception as e:
            if self.log:
                self.log.error("Error loading config.json:", e)
            self._config = {}

    def get_config(self, key, default=None):
        value = self._config.get(key, default)
        if self.log:
            self.log.debug(f"[ConfigManager] get_config('{key}') -> {value}")
        return value

    def set_config(self, key, value):
        self._config[key] = value
        if self.log:
            self.log.debug(f"[ConfigManager] set_config('{key}', {value})")
        self.save()

    def save(self):
        if self.log:
            self.log.info(f"[ConfigManager] Saving config to {self.filename}: {self._config}")
        try:
            with open(self.filename, "w") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            if self.log:
                self.log.error("Error saving config.json:", e)

    def __del__(self):
        if self.log:
            self.log.debug("[ConfigManager] __del__ called, saving config.")
        self.save()
