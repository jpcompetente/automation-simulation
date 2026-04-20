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