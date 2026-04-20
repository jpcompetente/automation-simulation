import json

class ConfigLoader:
    def __init__(self, file):
        self.file = file

    def load(self):
        with open(self.file, "r") as f:
            return json.load(f)