import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import json
import paho.mqtt.client as mqtt

from core.state_machine import StateMachine
from core.controller import Controller

from devices.sensors.temperature import TemperatureSensor
from devices.sensors.proximity import ProximitySensor

from devices.actuators.motor import Motor
from devices.actuators.conveyor import Conveyor
from devices.actuators.alarm import Alarm

# MQTT
BROKER = "127.0.0.1"
PORT = 1885
TOPIC_PUB = "plc/simulation/data"
TOPIC_SUB = "plc/simulation/control"

# DEVICES
temp = TemperatureSensor("Temp")
prox = ProximitySensor("Proximity")

motor = Motor()
conveyor = Conveyor()
alarm = Alarm()

# CORE
sm = StateMachine()
controller = Controller(motor, conveyor, alarm)

# KPI
run_time = 0
stop_time = 0
item_count = 0
accepted_count = 0
rejected_count = 0
error_count = 0
warning_count = 0

last_item = False
last_state = "IDLE"
command = "RESET"

# ERROR LOCK
error_locked = False
error_message = ""

# RESET FUNCTION
def reset_kpi():
    global run_time, stop_time, item_count
    global accepted_count, rejected_count, error_count, warning_count
    global last_item, last_state, error_locked, error_message

    run_time = 0
    stop_time = 0
    item_count = 0
    accepted_count = 0
    rejected_count = 0
    error_count = 0
    warning_count = 0

    error_locked = False
    error_message = ""

    last_item = False
    last_state = "IDLE"

    print("🔄 RESET DONE")

# MQTT
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Connected")
    client.subscribe(TOPIC_SUB)

def on_message(client, userdata, msg):
    global command, error_locked, error_message

    command = msg.payload.decode()
    print("COMMAND:", command)

    if command == "RESET":
        reset_kpi()
        alarm.deactivate()
        error_locked = False
        error_message = ""

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

print("=== RUNNING ===")

while True:

    # CURRENT STATE
    state = sm.state

    # READ SENSORS
    temperature = temp.read(state)
    item_detected = prox.detect(state)

    # 🔥 SAFETY LOGIC (MAIN FIX)
    if error_locked:
        state = "ERROR"

    else:
        if temperature > 60:
            warning_count += 1

            # If 50 warnings are reached, log as error
            if warning_count >= 50 and error_count < 100:
                error_count += 1

            # If 100 errors are reached, lock the system
            if error_count >= 100:
                error_locked = True
                error_message = "LOCKED - 100 Errors Reached"
                state = "ERROR"

                motor.stop()
                conveyor.stop()
                alarm.activate()

                print("🔥 SYSTEM LOCKED - 100 Errors Reached")

            elif warning_count >= 50:
                error_message = "Warning Threshold Reached"
                state = "ERROR"  # Optional: set to ERROR state if warnings are high enough

        else:
            state = sm.transition(command, temperature)
            controller.update(state, item_detected)

            if state != "ERROR":
                alarm.deactivate()

    # TIME
    if state == "RUN":
        run_time += 1
    else:
        stop_time += 1

    # ITEM COUNT
    if item_detected and not last_item:
        item_count += 1

        if state == "RUN":
            accepted_count += 1
        elif state == "ERROR":
            rejected_count += 1

    last_item = item_detected

    # ERROR COUNT TRACK
    if state == "ERROR" and last_state != "ERROR":
        error_count += 1

    last_state = state

    # CALCULATIONS
    total_time = run_time + stop_time

    rate = (item_count / run_time * 60) if run_time > 0 else 0
    error_percent = (error_count / item_count * 100) if item_count > 0 else 0
    efficiency = (run_time / total_time * 100) if total_time > 0 else 0
    yield_percent = (accepted_count / item_count * 100) if item_count > 0 else 0

    # DATA SEND
    data = {
        "state": state,
        "temperature": temperature,
        "motor": motor.status(),
        "conveyor": conveyor.status(),
        "alarm": alarm.status(),
        "item_detected": item_detected,

        "run_time": run_time,
        "stop_time": stop_time,
        "item_count": item_count,
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "error_count": error_count,
        "warning_count": warning_count,

        "rate": rate,
        "error_percent": error_percent,
        "efficiency": efficiency,
        "yield_percent": yield_percent,

        "error_message": error_message,
        "error_locked": error_locked
    }

    client.publish(TOPIC_PUB, json.dumps(data))

    print(data)

    time.sleep(1)