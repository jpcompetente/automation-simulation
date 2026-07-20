# Automation Simulation System

Industrial PLC simulation with MQTT-based dashboard, state machine control, and KPI tracking.

## Architecture

- **Mosquitto** — MQTT broker (Windows service, auto-starts)
- **app/runner.py** — main control loop (publisher): reads sensors, runs decision engine, publishes state via MQTT
- **dashboard/dashboard.py** — Tkinter UI (subscriber): displays live system state, sends START/STOP/RESET commands
- **settings.py** — centralized config (BROKER, PORT, MQTT topics)
- **config/logic_config.json** — temperature thresholds (high_threshold, warning_limit, error_limit)
- **config/devices.json** — sensor/actuator registry

## Setup (first time)

```powershell
# 1. Create venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify Mosquitto broker is running
Get-Service mosquitto
# If not "Running", start it (as Administrator):
Start-Service mosquitto
```

## Running the System

Open **two terminals**, both with venv activated:

**Terminal 1 — Runner (control loop + publisher):**
```powershell
python -m app.runner
```

**Terminal 2 — Dashboard (UI):**
```powershell
python -m dashboard.dashboard
```

## Notes

- Broker: `127.0.0.1:1883`
- Publish topic: `plc/simulation/data` | Subscribe/control topic: `plc/simulation/control`
- ERROR state requires manual RESET (does not auto-clear when temperature returns to normal — intentional safety behavior)
- Temperature threshold is configurable via `config/logic_config.json` → `high_threshold`
