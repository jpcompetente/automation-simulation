Automation_clean_ver/
│
├── app/
│   └── simulation.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json

from core.state_machine import StateMachine
from core.controller import Controller

from infrastructure.mqtt.mqtt_client import MQTTClient
from managers.device_manager import DeviceManager
from infrastructure.config.config_loader import load_devices_from_config
from core.watchdog import Watchdog
from core.validator import Validator
from infrastructure.logging.file_logger import FileLogger
from managers.system_manager import SystemManager
from domain.kpi_manager import KPIManager

BROKER = "127.0.0.1"
PORT = 1885
TOPIC_PUB = "plc/simulation/data"
TOPIC_SUB = "plc/simulation/control"

# DEVICE MANAGER
devices = DeviceManager()
load_devices_from_config(devices)

# ACCESS
temp = devices.get_sensor("temp")
prox = devices.get_sensor("prox")

motor = devices.get_actuator("motor")
conveyor = devices.get_actuator("conveyor")
alarm = devices.get_actuator("alarm")

# CORE
sm = StateMachine()
controller = Controller(motor, conveyor, alarm)
system = SystemManager(sm, controller)

# WATCHDOG + LOGGER
watchdog = Watchdog(timeout=5)
logger = FileLogger()
last_logged_error = ""

# KPI
kpi = KPIManager()

command = ""

# ERROR SYSTEM
error_locked = False
error_message = ""


def reset_kpi():
    global error_locked, error_message
    kpi.reset()
    error_locked = False
    error_message = ""


# MQTT CLIENT
mqtt_client = MQTTClient(
    broker=BROKER,
    port=PORT,
    topic_sub=TOPIC_SUB,
    topic_pub=TOPIC_PUB
)

mqtt_client.start()


def on_message(client, userdata, msg):
    global command

    command = msg.payload.decode()

    if command == "RESET":
        reset_kpi()
        alarm.deactivate()
        print("🔄 SYSTEM RESET → WAITING FOR START")


mqtt_client.client.on_message = on_message

print("=== RUNNING SYSTEM ===")

while True:

    watchdog.feed()

    state = sm.state

    temperature = temp.read(state)
    item_detected = prox.detect(state)

    # VALIDATION
    if not Validator.validate_temperature(temperature):

        state = "ERROR"
        error_message = "INVALID SENSOR DATA"

        if error_message != last_logged_error:
            logger.log(error_message)
            last_logged_error = error_message

        motor.stop()
        conveyor.stop()
        alarm.activate()
        item_detected = False

    else:
        if error_locked:
            state = "ERROR"
            error_message = "LOCKED - 100 Errors Reached"

            if error_message != last_logged_error:
                logger.log(error_message)
                last_logged_error = error_message

            motor.stop()
            conveyor.stop()
            alarm.activate()
            item_detected = False

        else:
            if temperature > 60:
                kpi.error_count += 1
                kpi.warning_count += 1

                state = "ERROR"
                error_message = "HIGH TEMPERATURE DETECTED"

                if error_message != last_logged_error:
                    logger.log(error_message)
                    last_logged_error = error_message

                if kpi.warning_count >= 50:
                    error_message = "WARNING: High Temperature"

                if kpi.error_count >= 100:
                    error_locked = True
                    error_message = "LOCKED - 100 Errors Reached"

            else:
                error_message = ""

                state = system.process(command, temperature, item_detected)
                command = ""

    # KPI UPDATE
    kpi.update(state, item_detected, error_locked)

    metrics = kpi.compute()

    # HEADER CONTROL
    header_state = state
    if not error_locked and kpi.error_count < 50 and state == "ERROR":
        header_state = "RUN"

    data = {
        "state": state,
        "header_state": header_state,
        "temperature": temperature,
        "motor": motor.status(),
        "conveyor": conveyor.status(),
        "alarm": alarm.status(),
        "item_detected": item_detected,

        "run_time": kpi.run_time,
        "stop_time": kpi.stop_time,
        "item_count": kpi.item_count,
        "accepted_count": kpi.accepted_count,
        "rejected_count": kpi.rejected_count,
        "error_count": kpi.error_count,
        "warning_count": kpi.warning_count,

        "rate": metrics["rate"],
        "error_percent": metrics["error_percent"],
        "efficiency": metrics["efficiency"],
        "yield_percent": metrics["yield_percent"],

        "error_message": error_message,
        "error_locked": error_locked
    }

    mqtt_client.send_message(json.dumps(data))

    if not watchdog.is_alive():
        print("⚠ SYSTEM NOT RESPONDING")

    time.sleep(1)
│
├── config/
│   ├── __init__.py
│   ├── devices.json
{
  "sensors": [
    {
      "name": "temp",
      "module": "devices.sensors.temperature",
      "class": "TemperatureSensor"
    },
    {
      "name": "prox",
      "module": "devices.sensors.proximity",
      "class": "ProximityDevice"
    }
  ],
  "actuators": [
    {
      "name": "motor",
      "module": "devices.actuators.motor",
      "class": "Motor"
    },
    {
      "name": "conveyor",
      "module": "devices.actuators.conveyor",
      "class": "Conveyor"
    },
    {
      "name": "alarm",
      "module": "devices.actuators.alarm",
      "class": "Alarm"
    }
  ]
}
│   ├── system_config.json
{
  "mode": "SIMULATION"
}
│   └── system_loader.py
import json

def get_system_mode(config_path="config/system_config.json"):
    with open(config_path, "r") as f:
        config = json.load(f)

    return config.get("mode", "SIMULATION")
│ 
├── core/
│   ├── __init__.py
│   ├── controller.py
class Controller:

    def __init__(self, motor, conveyor, alarm):
        self.motor = motor
        self.conveyor = conveyor
        self.alarm = alarm

    def update(self, state, item_detected):

        # 🔴 FULL STOP ONLY HERE
        if state == "LOCKED":
            self.motor.stop()
            self.conveyor.stop()
            self.alarm.activate()
            return

        # 🔥 ALWAYS RUN
        self.conveyor.start()
        self.alarm.deactivate()

        if item_detected:
            self.motor.start()
        else:
            self.motor.stop()
│   ├── file_logger.py
from datetime import datetime

class FileLogger:
    def __init__(self, filename="system.log"):
        self.filename = filename

    def log(self, message):
        with open(self.filename, "a") as f:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{time}] {message}\n")
│   └── logger.py
from datetime import datetime

class Logger:

    @staticmethod
    def log(data):
        time_now = datetime.now().strftime("%H:%M:%S")
        print(f"[{time_now}] {data}")
│   └── state_logger.py
class StateLogger:
    def __init__(self):
        self.history = []

    def log(self, state):
        self.history.append(state)

    def get_history(self):
        return self.history
│   └── state_machine.py
class StateMachine:
    IDLE = "IDLE"
    RUN = "RUN"
    ERROR = "ERROR"
    STOP = "STOP"

    def __init__(self):
        self.state = self.IDLE

    def get_state(self):
        return self.state

    def transition(self, command, temperature=None):

        # 🔥 GLOBAL RESET (works in ANY state)
        if command == "RESET":
            self.state = self.IDLE
            return self.state

        # 🔴 ERROR STATE LOCK
        if self.state == self.ERROR:
            return self.state

        # 🌡 TEMPERATURE ERROR
        if temperature is not None and temperature > 60:
            self.state = self.ERROR
            return self.state

        # ▶ NORMAL TRANSITIONS
        if command == "START":
            self.state = self.RUN

        elif command == "STOP":
            self.state = self.STOP

        return self.state
│   └── timer.py
import time

class Timer:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def elapsed(self):
        if self.start_time:
            return time.time() - self.start_time
        return 0

    def reset(self):
        self.start_time = None
│   └── validator.py
class Validator:
    @staticmethod
    def validate_temperature(value):
        if value < -10 or value > 150:
            return False
        return True
│   └── watchdog.py
import time

class Watchdog:
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.last_feed = time.time()

    def feed(self):
        self.last_feed = time.time()

    def is_alive(self):
        return (time.time() - self.last_feed) < self.timeout
│
├── dashboard/
│   └── dashboard.py
import tkinter as tk
import paho.mqtt.client as mqtt
import json
from datetime import datetime

# MQTT SETTINGS
BROKER = "127.0.0.1"
PORT = 1885
TOPIC_SUB = "plc/simulation/data"
TOPIC_PUB = "plc/simulation/control"

data = {}

# BLINK + LOG
blink_state = False
last_error_msg = ""

# ---------- UI ----------
root = tk.Tk()
root.title("Industrial PLC Dashboard")
root.geometry("600x700")

# HEADER
tk.Label(root, text="Industrial Automation System", font=("Arial", 18, "bold")).pack(pady=10)

# BIG STATUS
status_big = tk.Label(root, text="IDLE", font=("Arial", 32, "bold"))
status_big.pack()

# CONNECTION
conn_label = tk.Label(root, text="MQTT: CONNECTING...", fg="orange")
conn_label.pack()

# WARNING + ERROR
warning_label = tk.Label(root, text="Warnings: 0", font=("Arial", 12))
warning_label.pack()

error_message_label = tk.Label(root, text="Error: None", fg="red", font=("Arial", 12, "bold"))
error_message_label.pack()

# KPI FRAME
frame_kpi = tk.LabelFrame(root, text="KPI", padx=10, pady=5)
frame_kpi.pack(fill="x", padx=10, pady=8)

runtime_label = tk.Label(frame_kpi, text="Run Time: 0s")
runtime_label.pack(anchor="w")

stoptime_label = tk.Label(frame_kpi, text="Stop Time: 0s")
stoptime_label.pack(anchor="w")

itemcount_label = tk.Label(frame_kpi, text="Items: 0")
itemcount_label.pack(anchor="w")

accepted_label = tk.Label(frame_kpi, text="Accepted: 0")
accepted_label.pack(anchor="w")

rejected_label = tk.Label(frame_kpi, text="Rejected: 0")
rejected_label.pack(anchor="w")

errorcount_label = tk.Label(frame_kpi, text="Errors: 0")
errorcount_label.pack(anchor="w")

rate_label = tk.Label(frame_kpi, text="Rate: 0 item/min")
rate_label.pack(anchor="w")

errorperc_label = tk.Label(frame_kpi, text="Error %: 0%")
errorperc_label.pack(anchor="w")

efficiency_label = tk.Label(frame_kpi, text="Efficiency: 0%")
efficiency_label.pack(anchor="w")

yield_label = tk.Label(frame_kpi, text="Yield: 0%")
yield_label.pack(anchor="w")

# SYSTEM STATUS
frame_status = tk.LabelFrame(root, text="System Status", padx=10, pady=5)
frame_status.pack(fill="x", padx=10, pady=8)

state_label = tk.Label(frame_status, text="State: IDLE", font=("Arial", 14))
state_label.pack(anchor="w")

temp_label = tk.Label(frame_status, text="Temp: 0")
temp_label.pack(anchor="w")

# DEVICES
frame_devices = tk.LabelFrame(root, text="Devices", padx=10, pady=5)
frame_devices.pack(fill="x", padx=10, pady=8)

motor_label = tk.Label(frame_devices, text="Motor: OFF")
motor_label.pack(anchor="w")

conveyor_label = tk.Label(frame_devices, text="Conveyor: OFF")
conveyor_label.pack(anchor="w")

item_label = tk.Label(frame_devices, text="Item: NONE")
item_label.pack(anchor="w")

alarm_label = tk.Label(frame_devices, text="Alarm: OFF")
alarm_label.pack(anchor="w")

# CONTROLS
frame_controls = tk.LabelFrame(root, text="Controls", padx=10, pady=5)
frame_controls.pack(fill="x", padx=10, pady=8)

def send_command(cmd):
    try:
        client.publish(TOPIC_PUB, cmd)
        add_log(f"✔ Command Sent: {cmd}")
    except:
        add_log("⚠ MQTT not connected")

tk.Button(frame_controls, text="START", bg="green", fg="white", command=lambda: send_command("START")).pack(fill="x", pady=2)
tk.Button(frame_controls, text="STOP", bg="orange", command=lambda: send_command("STOP")).pack(fill="x", pady=2)
tk.Button(frame_controls, text="RESET", bg="gray", fg="white", command=lambda: send_command("RESET")).pack(fill="x", pady=2)

# LOGS
frame_logs = tk.LabelFrame(root, text="System Logs", padx=10, pady=5)
frame_logs.pack(fill="both", expand=True, padx=10, pady=8)

log_box = tk.Text(frame_logs, height=10)
log_box.pack(fill="both", expand=True)

# ---------- FUNCTIONS ----------

def get_color(state):
    return {"RUN": "green", "ERROR": "red", "STOP": "orange"}.get(state, "gray")

def safe_get(key, default=0):
    return data.get(key, default)

def update_display():
    global blink_state, last_error_msg

    header_state = safe_get("header_state", "IDLE")
    real_state = safe_get("state", "IDLE")

    status_big.config(text=header_state, fg=get_color(header_state))
    state_label.config(text=f"State: {real_state}", fg=get_color(real_state))
    temp_label.config(text=f"Temp: {safe_get('temperature')}")

    motor_label.config(text=f"Motor: {'🟢 ON' if safe_get('motor') else '⚫ OFF'}")
    conveyor_label.config(text=f"Conveyor: {'🟢 ON' if safe_get('conveyor') else '⚫ OFF'}")
    item_label.config(text=f"Item: {'📦 DETECTED' if safe_get('item_detected') else '— NONE'}")
    alarm_label.config(text=f"Alarm: {'🚨 ON' if safe_get('alarm') else 'OFF'}")

    runtime_label.config(text=f"Run Time: {safe_get('run_time')}s")
    stoptime_label.config(text=f"Stop Time: {safe_get('stop_time')}s")
    itemcount_label.config(text=f"Items: {safe_get('item_count')}")
    accepted_label.config(text=f"Accepted: {safe_get('accepted_count')}")
    rejected_label.config(text=f"Rejected: {safe_get('rejected_count')}")
    errorcount_label.config(text=f"Errors: {safe_get('error_count')}")

    rate_label.config(text=f"Rate: {safe_get('rate'):.2f} item/min")
    errorperc_label.config(text=f"Error %: {safe_get('error_percent'):.1f}%")
    efficiency_label.config(text=f"Efficiency: {safe_get('efficiency'):.1f}%")
    yield_label.config(text=f"Yield: {safe_get('yield_percent'):.1f}%")

    # 🔥 BLINKING WARNING
    warnings = safe_get("warning_count")
    if warnings >= 50:
        blink_state = not blink_state
        warning_label.config(fg="red" if blink_state else "black")
    else:
        warning_label.config(fg="black")

    warning_label.config(text=f"Warnings: {warnings}")

    # ERROR MESSAGE
    error_msg = safe_get("error_message", "")
    if error_msg:
        error_message_label.config(text=f"Error: {error_msg}", fg="red")

        if error_msg != last_error_msg:
            add_log(f"🚨 {error_msg}")
            last_error_msg = error_msg
    else:
        error_message_label.config(text="Error: None", fg="black")

def add_log(message):
    time_now = datetime.now().strftime("%H:%M:%S")
    log_box.insert(tk.END, f"[{time_now}] {message}\n")
    log_box.see(tk.END)

# 🔥 AUTO REFRESH LOOP
def loop():
    update_display()
    root.after(500, loop)

# ---------- MQTT ----------

def on_connect(client, userdata, flags, rc):
    conn_label.config(text="MQTT: CONNECTED", fg="green")
    client.subscribe(TOPIC_SUB)
    add_log("✅ Connected to MQTT")

def on_message(client, userdata, msg):
    global data
    try:
        data = json.loads(msg.payload.decode())
    except:
        print("Invalid data received")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    client.loop_start()
except:
    conn_label.config(text="MQTT: OFFLINE", fg="red")

# START LOOP
loop()

root.mainloop()
│
├── devices/
│   ├── __init__.py
│   │
│   ├── actuators/
│   │   ├── __init__.py
│   │   ├── alarm.py
from lib.actuators.alarm import Alarm as AlarmLib

class Alarm:
    def __init__(self):
        self.alarm = AlarmLib()

    def activate(self):
        self.alarm.activate()

    def deactivate(self):
        self.alarm.deactivate()

    def status(self):
        return self.alarm.status()
│   │   ├── conveyor.py
from lib.actuators.conveyor import Conveyor as ConveyorLib

class Conveyor:
    def __init__(self):
        self.conveyor = ConveyorLib()

    def start(self):
        self.conveyor.start()

    def stop(self):
        self.conveyor.stop()

    def status(self):
        return self.conveyor.status()
│   │   ├── digital_actuator.py
class DigitalActuator:
    def __init__(self, name):
        self.name = name
        self._status = False

    def activate(self):
        self._status = True

    def deactivate(self):
        self._status = False

    def status(self):
        return self._status
│   │   ├── motor.py
from lib.actuators.motor import Motor as MotorLib

class Motor:
    def __init__(self):
        self.motor = MotorLib()

    def start(self):
        self.motor.start()

    def stop(self):
        self.motor.stop()

    def status(self):
        return self.motor.status()
│   │   ├── motor_real.py
class Motor:
    def __init__(self):
        self._status = False

    def activate(self):
        self._status = True
        print("[REAL] Motor ON")

    def deactivate(self):
        self._status = False
        print("[REAL] Motor OFF")

    def status(self):
        return self._status
│   │   └── valve.py
from devices.base.actuator_base import BaseActuator

class Valve(BaseActuator):

    def __init__(self):
        super().__init__("Valve")

    def open(self):
        self.start()

    def close(self):
        self.stop()
│   │
│   ├── base/
│   │   ├── __init__.py
│   │   ├── actuator_base.py
class BaseActuator:
    def __init__(self, name):
        self.name = name
        self._status = False

    def start(self):
        self._status = True

    def stop(self):
        self._status = False

    def status(self):
        return self._status
│   │   └── sensor_base.py
class BaseSensor:
    def __init__(self, name):
        self.name = name

    def read(self, state=None):
        raise NotImplementedError("Sensor read() not implemented")
│   │
│   └── sensors/
│       ├── __init__.py
│       ├── analog_sensor.py
class AnalogSensor:
    def __init__(self, name, min_val=0, max_val=100):
        self.name = name
        self.value = min_val
        self.min = min_val
        self.max = max_val

    def read(self, state=None):
        import random
        self.value += random.uniform(-1, 2)

        if self.value < self.min:
            self.value = self.min
        if self.value > self.max:
            self.value = self.max

        return round(self.value, 2)
│       ├── digital_sensor.py
class DigitalSensor:
    def __init__(self, name):
        self.name = name
        self.state = False

    def read(self, system_state=None):
        import random
        self.state = random.choice([True, False])
        return self.state
│       ├── pressure.py
from devices.base.sensor_base import BaseSensor
import random

class PressureSensor(BaseSensor):

    def read(self, state=None):
        if state == "RUN":
            return random.randint(70, 120)
        return random.randint(30, 60)
│       ├── proximity.py
from lib.sensors.proximity import ProximitySensor

class ProximityDevice:
    def __init__(self):
        self.sensor = ProximitySensor()

    def detect(self, state):
        return self.sensor.detect(state)
│       ├── temperature.py
from lib.sensors.temperature import TemperatureSensor

class TempSensor:
    def __init__(self):
        self.sensor = TemperatureSensor()

    def read(self, state):
        return self.sensor.read(state)from lib.sensors.temperature import TemperatureSensor

class TempSensor:
    def __init__(self):
        self.sensor = TemperatureSensor()

    def read(self, state):
        return self.sensor.read(state)
│       ├── temperature_real.py
class TemperatureSensor:
    def __init__(self, name):
        self.name = name
        self.temp = 30

    def read(self, state=None):
        # simulate realistic behavior
        if state == "RUN":
            self.temp += 0.5
        elif state == "ERROR":
            self.temp += 1

        # clamp values
        if self.temp > 100:
            self.temp = 100

        return self.temp
│       └── vibration.py
from devices.base.sensor_base import BaseSensor
import random

class VibrationSensor(BaseSensor):

    def read(self, state=None):
        if state == "RUN":
            return random.randint(3, 10)
        return random.randint(0, 2)
│
├── domain/
│   └── kpi_manager.py
class KPIManager:
    def __init__(self):
        self.run_time = 0
        self.stop_time = 0
        self.item_count = 0
        self.accepted_count = 0
        self.rejected_count = 0
        self.error_count = 0
        self.warning_count = 0

        self.last_item = False

    def reset(self):
        self.__init__()

    def update(self, state, item_detected, error_locked):
        # TIME
        if not error_locked:
            self.run_time += 1
        else:
            self.stop_time += 1

        # ITEM
        if item_detected and not self.last_item:
            self.item_count += 1

            if state == "RUN":
                self.accepted_count += 1
            else:
                self.rejected_count += 1

        self.last_item = item_detected

    def compute(self):
        total_time = self.run_time + self.stop_time

        rate = (self.item_count / self.run_time * 60) if self.run_time > 0 else 0
        error_percent = (self.error_count / self.item_count * 100) if self.item_count > 0 else 0
        efficiency = (self.run_time / total_time * 100) if total_time > 0 else 0
        yield_percent = (self.accepted_count / self.item_count * 100) if self.item_count > 0 else 0

        return {
            "rate": rate,
            "error_percent": error_percent,
            "efficiency": efficiency,
            "yield_percent": yield_percent
        }
│
├── infrastructure/
│   └── config
│   │   └── __init__.py
│   │   └── config_loader.py
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
│
│   └── logging
│   │   └── __init__.py
│   │   └── file_logger.py
from datetime import datetime

class FileLogger:
    def __init__(self, filename="system.log"):
        self.filename = filename

    def log(self, message):
        with open(self.filename, "a") as f:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{time}] {message}\n")
│
│   └── mqtt
│   │   └── __init__.py
│   │   └── mqtt_client.py
import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port, topic_sub, topic_pub):
        # Initialize MQTT client, setting broker, port, and topics
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub

        # Initialize callback functions for connect and message
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        """
        Called when the client connects to the broker.
        """
        print(f"Connected to broker with result code {rc}")
        client.subscribe(self.topic_sub)  # Subscribe to the topic when connected

    def on_message(self, client, userdata, msg):
        """
        Called when a message is received on the subscribed topic.
        """
        try:
            payload = msg.payload.decode()  # Decode the message payload
            print(f"Message received: {payload}")
        except Exception as e:
            print(f"Error decoding message: {e}")

    def send_message(self, message):
        """
        Send a message to the publisher topic.
        """
        try:
            self.client.publish(self.topic_pub, message)
            print(f"Message sent: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")

    def start(self):
        """
        Connect to the broker and start the loop to listen for messages.
        """
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()  # Start the loop to listen for incoming messages
        except Exception as e:
            print(f"Error connecting to broker: {e}")

    def stop(self):
        """
        Stop the MQTT client loop.
        """
        self.client.loop_stop()
        print("MQTT loop stopped")
│
├── lib/
│   ├── actuators/
│   │   ├── __init__.py
│   │   ├── alarm.py
class Alarm:
    def __init__(self):
        self.active = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def status(self):
        return self.active
│   │   ├── base_actuator.py
class BaseActuator:
    def __init__(self, name="Actuator"):
        self.name = name
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def status(self):
        return self._running
│   │   ├── conveyor.py
from .base_actuator import BaseActuator

class Conveyor(BaseActuator):
    def __init__(self, name="Conveyor"):
        super().__init__(name)
│   │   ├── motor.py
from .base_actuator import BaseActuator

class Motor(BaseActuator):
    def __init__(self, name="Motor"):
        super().__init__(name)
│   │   └── valve.py
from .base_actuator import BaseActuator

class Valve(BaseActuator):
    def open(self):
        self.start()

    def close(self):
        self.stop()
│   │
│   ├── communication/
│   │   ├── modbus_client.py
class ModbusClient:
    def __init__(self, host="127.0.0.1", port=502):
        self.host = host
        self.port = port
        self.connected = False

    def connect(self):
        print(f"[Modbus] Connecting to {self.host}:{self.port}")
        self.connected = True

    def read_register(self, address):
        if not self.connected:
            raise Exception("Modbus not connected")

        # 🔥 placeholder (simulate)
        return 0

    def write_register(self, address, value):
        if not self.connected:
            raise Exception("Modbus not connected")

        print(f"[Modbus] Write {value} to {address}")

    def disconnect(self):
        self.connected = False
        print("[Modbus] Disconnected")
│   │   ├── mqtt_client.py
class MQTTClient:
    def publish(self, topic, message):
        pass

    def subscribe(self, topic):
        pass
│   │   └── opcua_client.py
class OPCUAClient:
    def __init__(self, endpoint="opc.tcp://localhost:4840"):
        self.endpoint = endpoint
        self.connected = False

    def connect(self):
        print(f"[OPCUA] Connecting to {self.endpoint}")
        self.connected = True

    def read(self, node):
        if not self.connected:
            raise Exception("OPCUA not connected")

        # 🔥 placeholder
        return None

    def write(self, node, value):
        if not self.connected:
            raise Exception("OPCUA not connected")

        print(f"[OPCUA] Write {value} to {node}")

    def disconnect(self):
        self.connected = False
        print("[OPCUA] Disconnected")
│   │
│   ├── control/
│   │   ├── pid_controller.py
class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, setpoint, value):
        error = setpoint - value
        self.integral += error
        derivative = error - self.prev_error

        output = (
            self.kp * error +
            self.ki * self.integral +
            self.kd * derivative
        )

        self.prev_error = error
        return output

    def reset(self):
        self.integral = 0
        self.prev_error = 0
│   │   ├── state_machine_base.py
class StateMachineBase:
    def __init__(self, initial_state):
        self.state = initial_state
        self.transitions = {}

    def add_transition(self, from_state, condition, to_state):
        """
        condition = function(context) -> True/False
        """
        if from_state not in self.transitions:
            self.transitions[from_state] = []

        self.transitions[from_state].append((condition, to_state))

    def update(self, context):
        """
        context = dictionary (data)
        """
        if self.state not in self.transitions:
            return self.state

        for condition, new_state in self.transitions[self.state]:
            if condition(context):
                self.state = new_state
                break

        return self.state

    def get_state(self):
        return self.state

    def reset(self, state):
        self.state = state
│   │   └── timer.py
import time

class Timer:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def elapsed(self):
        if self.start_time:
            return time.time() - self.start_time
        return 0

    def reset(self):
        self.start_time = None
│   │
│   ├── core/
│   │   ├── alarm_manager.py
class AlarmManager:
    def __init__(self):
        self.active_alarms = set()

    def trigger(self, message):
        self.active_alarms.add(message)

    def clear(self, message=None):
        if message:
            self.active_alarms.discard(message)
        else:
            self.active_alarms.clear()

    def has_active(self):
        return len(self.active_alarms) > 0

    def get_all(self):
        return list(self.active_alarms)
│   │   ├── data_processor.py
class DataProcessor:
    def filter_noise(self, value, threshold=0.5):
        if abs(value) < threshold:
            return 0
        return value

    def normalize(self, value, min_val, max_val):
        if max_val == min_val:
            return 0
        return (value - min_val) / (max_val - min_val)

    def clamp(self, value, min_val, max_val):
        return max(min_val, min(value, max_val))
│   │   ├── decision_engine.py
class DecisionEngine:
    def decide(self, context):
        """
        context = {
            "temperature": int,
            "item_detected": bool,
            "error": bool
        }
        """
        if context.get("error"):
            return "STOP"

        if context.get("temperature", 0) > 80:
            return "WARNING"

        if context.get("item_detected"):
            return "RUN"

        return "IDLE"
│   │   ├── event_bus.py
class EventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event, callback):
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(callback)

    def publish(self, event, data=None):
        for callback in self.subscribers.get(event, []):
            callback(data)
│   │   ├── state_logger.py
class StateLogger:
    def __init__(self):
        self.history = []

    def log(self, state):
        self.history.append(state)

    def last(self):
        return self.history[-1] if self.history else None

    def all(self):
        return self.history
│   │   └── watchdog.py
import time

class Watchdog:
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.last_reset = time.time()

    def reset(self):
        self.last_reset = time.time()

    def is_alive(self):
        return (time.time() - self.last_reset) < self.timeout
│   │
│   ├── monitoring/
│   │   ├── kpi.py
class KPI:
    def __init__(self):
        self.run_time = 0
        self.stop_time = 0
        self.item_count = 0
        self.accepted = 0
        self.rejected = 0
        self.last_item = False

    def update(self, state, item_detected):
        if state == "RUN":
            self.run_time += 1
        else:
            self.stop_time += 1

        if item_detected and not self.last_item:
            self.item_count += 1
            if state == "RUN":
                self.accepted += 1
            else:
                self.rejected += 1

        self.last_item = item_detected

    def efficiency(self):
        total = self.run_time + self.stop_time
        return (self.run_time / total * 100) if total else 0
│   │   └── logger.py
from datetime import datetime

class Logger:
    def __init__(self, filename=None):
        self.filename = filename

    def log(self, message):
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{time_now}] {message}"

        if self.filename:
            with open(self.filename, "a") as f:
                f.write(log_msg + "\n")
        else:
            print(log_msg)
│   │
│   ├── sensors/
│   │   ├── __init__.py
│   │   ├── base_sensor.py
class BaseSensor:
    def __init__(self, name="Sensor"):
        self.name = name

    def read(self, state=None):
        raise NotImplementedError
│   │   ├── pressure.py
import random
from .base_sensor import BaseSensor

class PressureSensor(BaseSensor):
    def __init__(self, name="Pressure"):
        super().__init__(name)

    def read(self, state=None):
        if state == "RUN":
            return random.randint(70, 120)
        elif state == "ERROR":
            return random.randint(100, 150)
        return random.randint(30, 60)
│   │   ├── proximity.py
import random
from .base_sensor import BaseSensor

class ProximitySensor(BaseSensor):
    def detect(self, state=None):
        if state == "RUN":
            return random.choice([True, False, False])
        return False
│   │   ├── temperature.py
import random
from .base_sensor import BaseSensor

class TemperatureSensor(BaseSensor):
    def __init__(self, name="TempSensor"):
        super().__init__(name)
        self.base_temp = 30

    def read(self, state=None):
        if state == "RUN":
            return self.base_temp + random.randint(10, 35)
        elif state == "ERROR":
            return 70 + random.randint(0, 20)
        elif state == "STOP":
            return self.base_temp + random.randint(-3, 3)
        return self.base_temp + random.randint(-2, 5)
│   │   └── vibration.py
import random
from .base_sensor import BaseSensor

class VibrationSensor(BaseSensor):
    def __init__(self, name="Vibration"):
        super().__init__(name)

    def read(self, state=None):
        if state == "RUN":
            return random.randint(3, 10)
        elif state == "ERROR":
            return random.randint(8, 15)
        return random.randint(0, 2)
│   │
│   └── utils/
│       ├── config_loader.py
import json

class ConfigLoader:
    def __init__(self, file):
        self.file = file

    def load(self):
        with open(self.file, "r") as f:
            return json.load(f)
│       ├── helpers.py
import uuid

def generate_id():
    return str(uuid.uuid4())
│       └── validator.py
class Validator:
    @staticmethod
    def validate_temperature(temp):
        return 0 <= temp <= 120

    @staticmethod
    def validate_signal(signal):
        return signal in [True, False]
│
├── logs/
│   └── system.log
│
├── managers/
│   ├── config_loader.py
import json
import os


def load_devices_from_config(devices):

    # 🔥 FIX: GET PROJECT ROOT PATH
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_path = os.path.join(BASE_DIR, "config", "devices.json")

    # 🔍 DEBUG (optional)
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
│   ├── device_manager.py
class DeviceManager:

    def __init__(self):
        self.sensors = {}
        self.actuators = {}

    # ---------- SENSORS ----------
    def add_sensor(self, name, sensor):
        self.sensors[name] = sensor

    def get_sensor(self, name):
        return self.sensors.get(name)

    # ---------- ACTUATORS ----------
    def add_actuator(self, name, actuator):
        self.actuators[name] = actuator

    def get_actuator(self, name):
        return self.actuators.get(name)
│   └── system_manager.py
class SystemManager:
    def __init__(self, state_machine, controller):
        self.sm = state_machine
        self.controller = controller

    def process(self, command, temperature, item_detected):
        # 🔥 STATE TRANSITION
        state = self.sm.transition(command, temperature)
        self.sm.state = state

        # 🔥 CONTROL DEVICES
        self.controller.update(state, item_detected)

        return state
│
├── .gitignore
├── command.json
├── config.py
├── data.json
├── README.md
├── system.log
└── test_devices.py
NEXT LEVEL (kung gusto mo maging SENIOR LEVEL)

Sabihin mo lang, tutulungan kita gawin:

✅ Clean Architecture version (hexagonal)
✅ PLC-style ladder simulation logic
✅ Real OPC UA / Modbus integration
✅ Dockerized system
✅ Web dashboard (React + FastAPI)