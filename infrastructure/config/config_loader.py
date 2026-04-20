import json
import os


def load_devices_from_config(devices):
    """
    Load sensors and actuators from config/devices.json
    """

    # 🔥 GET PROJECT ROOT (IMPORTANT AFTER REFACTOR)
    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    config_path = os.path.join(BASE_DIR, "config", "devices.json")

    # 🔍 OPTIONAL DEBUG (pwede mo i-uncomment kung gusto mo makita path)
    # print("Loading config from:", config_path)

    # ---------- LOAD CONFIG ----------
    with open(config_path, "r") as f:
        config = json.load(f)

    # ---------- LOAD SENSORS ----------
    for s in config.get("sensors", []):
        try:
            module = __import__(s["module"], fromlist=[s["class"]])
            cls = getattr(module, s["class"])
            devices.add_sensor(s["name"], cls())
        except Exception as e:
            print(f"❌ Error loading sensor {s['name']}: {e}")

    # ---------- LOAD ACTUATORS ----------
    for a in config.get("actuators", []):
        try:
            module = __import__(a["module"], fromlist=[a["class"]])
            cls = getattr(module, a["class"])
            devices.add_actuator(a["name"], cls())
        except Exception as e:
            print(f"❌ Error loading actuator {a['name']}: {e}")