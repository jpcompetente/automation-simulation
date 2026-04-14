import tkinter as tk
import paho.mqtt.client as mqtt
import json
from datetime import datetime

# MQTT SETTINGS
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_SUB = "plc/simulation/data"
TOPIC_PUB = "plc/simulation/control"

data = {
    "state": "IDLE",
    "temperature": 0,
    "motor": False,
    "rate": 0,
    "error_percent": 0,
    "efficiency": 0,
    "yield_percent": 0
}

# ---------- UI ----------
root = tk.Tk()
root.title("Industrial PLC Dashboard")
root.geometry("450x780")

# HEADER
tk.Label(root, text="Industrial Automation System",
         font=("Arial", 16, "bold")).pack(pady=10)

# BIG STATUS
status_big = tk.Label(root, text="IDLE", font=("Arial", 26, "bold"))
status_big.pack()

# CONNECTION
conn_label = tk.Label(root, text="MQTT: CONNECTING...", fg="orange")
conn_label.pack()

# ERROR MESSAGE
error_label = tk.Label(root, text="Error: None", fg="red")
error_label.pack()

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
    client.publish(TOPIC_PUB, cmd)
    add_log(f"✔ Command Sent: {cmd}")

tk.Button(frame_controls, text="START", bg="green", fg="white",
          command=lambda: send_command("START")).pack(fill="x", pady=2)

tk.Button(frame_controls, text="STOP", bg="orange",
          command=lambda: send_command("STOP")).pack(fill="x", pady=2)

tk.Button(frame_controls, text="RESET", bg="gray", fg="white",
          command=lambda: send_command("RESET")).pack(fill="x", pady=2)

# LOGS
frame_logs = tk.LabelFrame(root, text="System Logs", padx=10, pady=5)
frame_logs.pack(fill="both", expand=True, padx=10, pady=8)

log_box = tk.Text(frame_logs, height=10)
log_box.pack(fill="both", expand=True)

# ---------- FUNCTIONS ----------

def get_color(state):
    return {"RUN": "green", "ERROR": "red", "STOP": "orange"}.get(state, "gray")

def update_display():
    state = data.get("state", "IDLE")

    status_big.config(text=state, fg=get_color(state))
    state_label.config(text=f"State: {state}", fg=get_color(state))
    temp_label.config(text=f"Temp: {data.get('temperature')}")

    motor_label.config(text=f"Motor: {'🟢 ON' if data.get('motor') else '⚫ OFF'}")
    conveyor_label.config(text=f"Conveyor: {'🟢 ON' if data.get('conveyor') else '⚫ OFF'}")
    item_label.config(text=f"Item: {'📦 DETECTED' if data.get('item_detected') else '— NONE'}")
    alarm_label.config(text=f"Alarm: {'🚨 ON' if data.get('alarm') else 'OFF'}")

    # Update KPI values
    runtime_label.config(text=f"Run Time: {data.get('run_time')}s")
    stoptime_label.config(text=f"Stop Time: {data.get('stop_time')}s")
    itemcount_label.config(text=f"Items: {data.get('item_count')}")
    accepted_label.config(text=f"Accepted: {data.get('accepted_count')}")
    rejected_label.config(text=f"Rejected: {data.get('rejected_count')}")
    errorcount_label.config(text=f"Errors: {data.get('error_count')}")
    rate_label.config(text=f"Rate: {data.get('rate'):.2f} item/min")
    errorperc_label.config(text=f"Error %: {data.get('error_percent'):.1f}%")
    efficiency_label.config(text=f"Efficiency: {data.get('efficiency'):.1f}%")
    yield_label.config(text=f"Yield: {data.get('yield_percent'):.1f}%")

def add_log(message):
    time_now = datetime.now().strftime("%H:%M:%S")
    log_box.insert(tk.END, f"[{time_now}] {message}\n")
    log_box.see(tk.END)

# MQTT
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC_SUB)
    conn_label.config(text="MQTT: CONNECTED", fg="green")

def on_message(client, userdata, msg):
    global data
    data = json.loads(msg.payload.decode())
    root.after(0, update_display)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

root.mainloop()