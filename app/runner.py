import time
import json

from core.state_machine import StateMachine
from core.controller import Controller

from infrastructure.mqtt.mqtt_client import MQTTClient
from infrastructure.logging.file_logger import FileLogger
from infrastructure.config.config_loader import load_devices_from_config

from managers.device_manager import DeviceManager
from managers.system_manager import SystemManager

from domain.kpi_manager import KPIManager

from lib.core.watchdog import Watchdog

from app.services.error_manager import ErrorManager
from app.services.data_builder import build_payload
from app.services.decision_engine import DecisionEngine
from app.services.config_service import ConfigService
from app.services.alarm_manager import AlarmManager
from app.system_context import SystemContext


BROKER = "127.0.0.1"
PORT = 1885
TOPIC_PUB = "plc/simulation/data"
TOPIC_SUB = "plc/simulation/control"


def run_system():

    # ---------- CONTEXT ----------
    ctx = SystemContext()

    # ---------- DEVICES ----------
    ctx.devices = DeviceManager()
    load_devices_from_config(ctx.devices)

    ctx.temp = ctx.devices.get_sensor("temp")
    ctx.prox = ctx.devices.get_sensor("prox")

    ctx.motor = ctx.devices.get_actuator("motor")
    ctx.conveyor = ctx.devices.get_actuator("conveyor")
    ctx.alarm = ctx.devices.get_actuator("alarm")

    # ---------- CORE ----------
    ctx.state_machine = StateMachine()
    ctx.controller = Controller(ctx.motor, ctx.conveyor, ctx.alarm)
    ctx.system = SystemManager(ctx.state_machine, ctx.controller)

    # ---------- SERVICES ----------
    ctx.watchdog = Watchdog(timeout=5)
    ctx.logger = FileLogger()
    ctx.kpi = KPIManager()
    ctx.error = ErrorManager()

    # 🔥 CONFIG + ENGINE + ALARM
    ctx.config = ConfigService()
    ctx.engine = DecisionEngine(ctx.config)
    ctx.alarm_manager = AlarmManager()

    # ---------- MQTT ----------
    mqtt_client = MQTTClient(
        broker=BROKER,
        port=PORT,
        topic_sub=TOPIC_SUB,
        topic_pub=TOPIC_PUB
    )

    def on_message(_, __, msg):
        ctx.command = msg.payload.decode()

        if ctx.command == "RESET":
            ctx.kpi.reset()
            ctx.error.reset()
            ctx.alarm.deactivate()
            ctx.alarm_manager.clear_all()
            print("🔄 SYSTEM RESET → WAITING FOR START")

        elif ctx.command == "ACK":
            ctx.alarm_manager.acknowledge_all()
            print("✅ ALL ALARMS ACKNOWLEDGED")

    mqtt_client.start()
    mqtt_client.client.on_message = on_message

    print("=== RUNNING SYSTEM ===")

    # ---------- LOOP ----------
    while True:

        # 🔥 CONFIG RELOAD
        ctx.config.reload_if_changed()

        ctx.watchdog.feed()

        state = ctx.state_machine.get_state()

        temperature = ctx.temp.read(state)
        item_detected = ctx.prox.detect(state)

        # ---------- DECISION ENGINE ----------
        decision = ctx.engine.evaluate(ctx, temperature, item_detected)

        if decision["state"] == "ERROR":

            state = "ERROR"
            ctx.error.set_error(decision["message"], ctx.logger)

            ctx.motor.stop()
            ctx.conveyor.stop()
            ctx.alarm.activate()
            item_detected = False

        else:
            ctx.error.clear()

            state = ctx.system.process(ctx.command, temperature, item_detected)
            ctx.command = ""

        # ---------- KPI ----------
        ctx.kpi.update(state, item_detected)
        metrics = ctx.kpi.compute()

        # ---------- HEADER FIX ----------
        temp_cfg = ctx.config.get("temperature")

        header_state = state
        if not ctx.error.locked and ctx.kpi.error_count < temp_cfg["warning_limit"] and state == "ERROR":
            header_state = "RUN"

        # ---------- BUILD PAYLOAD ----------
        data = build_payload(
            state, header_state, temperature,
            ctx.motor, ctx.conveyor, ctx.alarm,
            item_detected, ctx.kpi, metrics, ctx.error,
            ctx  # 🔥 includes alarms + history
        )

        mqtt_client.send_message(json.dumps(data))

        # ---------- WATCHDOG ----------
        if not ctx.watchdog.is_alive():
            print("⚠ SYSTEM NOT RESPONDING")

        time.sleep(1)