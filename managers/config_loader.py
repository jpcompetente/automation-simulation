import json
import os


def load_devices_from_config(devices):

    #  FIX: GET PROJECT ROOT PATH
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_path = os.path.join(BASE_DIR, "config", "devices.json")

    # [DEBUG] DEBUG (optional)
    # print("Loading config from:", config_path)

    with open(config_path, "r") as f:
        config = json.load(f)

    # ---------- LOAD SENSORS ----------
    for s in config.get("sensors", []):
        module = __import__(s["module"], fromlist=[s["class"]])
        cls = getattr(module, s["class"])

        devices.add_sensor(s["name"], cls())

    # ---------- LOAD ACTUATORS ----------
    for a in config.get("actuators", []):
        module = __import__(a["module"], fromlist=[a["class"]])
        cls = getattr(module, a["class"])

        devices.add_actuator(a["name"], cls())