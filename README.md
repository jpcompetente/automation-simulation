# Automation Simulation System

Industrial PLC simulation with MQTT-based dashboard, state machine control, KPI tracking, and alarm management.

## Architecture

- **Mosquitto** — MQTT broker (Windows service, auto-starts on boot)
- **app/runner.py** — main control loop (publisher): reads sensors, runs decision engine, publishes state via MQTT, handles graceful shutdown
- **dashboard/dashboard.py** — Tkinter UI (subscriber): displays live system state, sends START/STOP/RESET/ACK commands
- **settings.py** — centralized config (BROKER, PORT, MQTT topics)
- **config/logic_config.json** — temperature thresholds (high_threshold, warning_limit, error_limit, min_valid, max_valid)
- **config/devices.json** — sensor/actuator registry
- **app/services/config_validator.py** — validates config files on startup before the system runs

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

To stop the runner safely, press **Ctrl+C** — it will stop the motor/conveyor/alarm and disconnect from MQTT cleanly before exiting.

## System Behavior

- **IDLE / STOP** — conveyor and motor are off; temperature gradually cools toward 28-35°
- **RUN** — conveyor runs, motor activates when an item is detected; temperature gradually rises toward 40-65°
- **ERROR** — triggered when temperature exceeds `high_threshold`; motor/conveyor stop, alarm activates; temperature rises toward 70-90° (simulating overheating)
- **ERROR recovery** — requires manual RESET command; does not auto-clear when temperature returns to normal (intentional safety behavior)
- Temperature changes gradually each second rather than jumping randomly, to simulate realistic thermal behavior
- Alarms are deduplicated (one active alarm per condition, not one per second) and alarm history is capped at 50 entries to prevent unbounded growth
- MQTT client auto-reconnects if the broker connection drops

## Configuration

- Broker: `127.0.0.1:1883`
- Publish topic: `plc/simulation/data` | Subscribe/control topic: `plc/simulation/control`
- Temperature threshold is configurable via `config/logic_config.json` → `high_threshold` (single source of truth — used by both the decision engine and the state machine)
- Config files are validated on startup; the system will fail fast with a clear error message if a required key is missing or invalid

## Troubleshooting

- **Dashboard shows "MQTT: OFFLINE"** — check that the Mosquitto service is running (`Get-Service mosquitto`)
- **Runner exits immediately with no output** — check `config/devices.json` and `config/logic_config.json` for syntax errors; validation errors are printed before the system starts
- **Import errors when running scripts directly** — always run via `python -m app.runner` or `python -m dashboard.dashboard` from the project root, not `python app\runner.py`
