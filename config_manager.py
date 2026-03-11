import json

class ConfigManager:
    def __init__(self, filename="config.json", log=None):
        self.filename = filename
        self.log = log
        self._config = {}
        try:
            with open(self.filename, "r") as f:
                self._config = json.load(f)
        except Exception as e:
            if self.log:
                self.log.error("Error loading config.json:", e)
            self._config = {}

    def get_config(self, key, default=None):
        return self._config.get(key, default)

    def set_config(self, key, value):
        self._config[key] = value
        self.save()

    def save(self):
        try:
            with open(self.filename, "w") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            if self.log:
                self.log.error("Error saving config.json:", e)

    def __del__(self):
        self.save()
