import json

def get_system_mode(config_path="config/system_config.json"):
    with open(config_path, "r") as f:
        config = json.load(f)

    return config.get("mode", "SIMULATION")