import tkinter as tk
import paho.mqtt.client as mqtt
import json
from datetime import datetime

from settings import BROKER, PORT

TOPIC_SUB = "plc/simulation/data"
TOPIC_PUB = "plc/simulation/control"

data = {}

blink_state = False
last_error_msg = ""

# ---------- UI ----------
root = tk.Tk()
root.title("Industrial PLC Dashboard")
root.geometry("600x750")

# 🔥 SCROLLABLE
container = tk.Frame(root)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container)
scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ---------- CONTENT ----------

tk.Label(scrollable_frame, text="Industrial Automation System", font=("Arial", 18, "bold")).pack(pady=10)

status_big = tk.Label(scrollable_frame, text="IDLE", font=("Arial", 32, "bold"))
status_big.pack()

conn_label = tk.Label(scrollable_frame, text="MQTT: CONNECTING...", fg="orange")
conn_label.pack()

warning_label = tk.Label(scrollable_frame, text="Warnings: 0")
warning_label.pack()

error_message_label = tk.Label(scrollable_frame, text="Error: None", fg="red")
error_message_label.pack()

# KPI
frame_kpi = tk.LabelFrame(scrollable_frame, text="KPI")
frame_kpi.pack(fill="x", padx=10, pady=8)

runtime_label = tk.Label(frame_kpi)
runtime_label.pack(anchor="w")

stoptime_label = tk.Label(frame_kpi)
stoptime_label.pack(anchor="w")

itemcount_label = tk.Label(frame_kpi)
itemcount_label.pack(anchor="w")

accepted_label = tk.Label(frame_kpi)
accepted_label.pack(anchor="w")

rejected_label = tk.Label(frame_kpi)
rejected_label.pack(anchor="w")

errorcount_label = tk.Label(frame_kpi)
errorcount_label.pack(anchor="w")

rate_label = tk.Label(frame_kpi)
rate_label.pack(anchor="w")

errorperc_label = tk.Label(frame_kpi)
errorperc_label.pack(anchor="w")

efficiency_label = tk.Label(frame_kpi)
efficiency_label.pack(anchor="w")

yield_label = tk.Label(frame_kpi)
yield_label.pack(anchor="w")

# STATUS
frame_status = tk.LabelFrame(scrollable_frame, text="System Status")
frame_status.pack(fill="x", padx=10, pady=8)

state_label = tk.Label(frame_status, font=("Arial", 12, "bold"))
state_label.pack(anchor="w")

temp_label = tk.Label(frame_status)
temp_label.pack(anchor="w")

# DEVICES
frame_devices = tk.LabelFrame(scrollable_frame, text="Devices")
frame_devices.pack(fill="x", padx=10, pady=8)

motor_label = tk.Label(frame_devices)
motor_label.pack(anchor="w")

conveyor_label = tk.Label(frame_devices)
conveyor_label.pack(anchor="w")

item_label = tk.Label(frame_devices)
item_label.pack(anchor="w")

alarm_label = tk.Label(frame_devices)
alarm_label.pack(anchor="w")

# ACTIVE ALARMS
frame_alarms = tk.LabelFrame(scrollable_frame, text="Active Alarms")
frame_alarms.pack(fill="x", padx=10, pady=8)

alarm_list_label = tk.Label(frame_alarms, text="No active alarms", fg="green", justify="left")
alarm_list_label.pack(anchor="w")

# 🔥 ACK BUTTON
def ack_all():
    try:
        client.publish(TOPIC_PUB, "ACK")
        add_log("✔ ACK sent")
    except:
        add_log("⚠ MQTT not connected")

tk.Button(frame_alarms, text="ACK ALL", bg="yellow", command=ack_all).pack(fill="x", pady=3)

# HISTORY
frame_history = tk.LabelFrame(scrollable_frame, text="Alarm History")
frame_history.pack(fill="x", padx=10, pady=8)

history_box = tk.Text(frame_history, height=5)
history_box.pack(fill="x")

# CONTROLS
frame_controls = tk.LabelFrame(scrollable_frame, text="Controls")
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
frame_logs = tk.LabelFrame(scrollable_frame, text="System Logs")
frame_logs.pack(fill="x", padx=10, pady=8)

log_box = tk.Text(frame_logs, height=8)
log_box.pack(fill="x")

# ---------- FUNCTIONS ----------

def get_color(state):
    return {
        "RUN": "green",
        "ERROR": "red",
        "STOP": "orange"
    }.get(state, "gray")


def safe_get(key, default=0):
    return data.get(key, default)


def update_display():
    header_state = safe_get("header_state", "IDLE")
    real_state = safe_get("state", "IDLE")

    status_big.config(text=header_state, fg=get_color(header_state))

    # 🔥 FIXED STATE COLOR
    state_label.config(
        text=f"State: {real_state}",
        fg=get_color(real_state)
    )

    temp_label.config(text=f"Temp: {safe_get('temperature')}")

    motor_label.config(text=f"Motor: {'ON' if safe_get('motor') else 'OFF'}")
    conveyor_label.config(text=f"Conveyor: {'ON' if safe_get('conveyor') else 'OFF'}")
    item_label.config(text=f"Item: {'DETECTED' if safe_get('item_detected') else 'NONE'}")
    alarm_label.config(text=f"Alarm: {'ON' if safe_get('alarm') else 'OFF'}")

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

    warning_label.config(text=f"Warnings: {safe_get('warning_count')}")
    error_message_label.config(text=f"Error: {safe_get('error_message')}")

    # ACTIVE ALARMS
    alarms = data.get("alarms", [])
    if alarms:
        txt = ""
        for a in alarms:
            icon = "⚠" if a.get("ack") else "🚨"
            txt += f"{icon} {a['message']} ({a['priority']})\n"

        color = "orange" if all(a.get("ack") for a in alarms) else "red"
        alarm_list_label.config(text=txt, fg=color)
    else:
        alarm_list_label.config(text="No active alarms", fg="green")

    # HISTORY
    history = data.get("alarm_history", [])
    new_text = ""

    for a in history[-10:]:
        icon = "⚠" if a.get("ack") else "🚨"
        new_text += f"[{a['timestamp']}] {icon} {a['message']}\n"

    if history_box.get(1.0, tk.END) != new_text:
        history_box.delete(1.0, tk.END)
        history_box.insert(tk.END, new_text)


def add_log(message):
    t = datetime.now().strftime("%H:%M:%S")
    log_box.insert(tk.END, f"[{t}] {message}\n")
    log_box.see(tk.END)


def loop():
    update_display()
    root.after(500, loop)


# MQTT
def on_connect(client, userdata, flags, rc):
    conn_label.config(text="MQTT: CONNECTED", fg="green")
    client.subscribe(TOPIC_SUB)


def on_message(client, userdata, msg):
    global data
    try:
        data = json.loads(msg.payload.decode())
    except:
        pass


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

loop()
root.mainloop()
