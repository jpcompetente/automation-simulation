import json
import os
import time

class ConfigService:

    def __init__(self):
        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )

        self.path = os.path.join(base_dir, "config", "logic_config.json")
        self.last_modified = 0
        self.config = {}

        self.load()

    def load(self):
        with open(self.path, "r") as f:
            self.config = json.load(f)

        self.last_modified = os.path.getmtime(self.path)

    def reload_if_changed(self):
        current_modified = os.path.getmtime(self.path)

        if current_modified != self.last_modified:
            print("🔄 Config reloaded!")
            self.load()

    def get(self, key):
        return self.config.get(key, {})