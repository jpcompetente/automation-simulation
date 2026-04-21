import time


class DecisionEngine:

    def __init__(self, config_service):
        self.config_service = config_service

    def evaluate(self, ctx, temperature, item_detected):

        config = self.config_service.get("temperature")

        # 🔴 INVALID SENSOR
        if temperature < config["min_valid"] or temperature > config["max_valid"]:
            return {"state": "ERROR", "message": "INVALID SENSOR DATA"}

        # 🔒 LOCKED SYSTEM
        if ctx.error.locked:
            return {"state": "ERROR", "message": "LOCKED - 100 Errors Reached"}

        # 🌡 HIGH TEMP
        if temperature > config["high_threshold"]:

            ctx.kpi.error_count += 1
            ctx.kpi.warning_count += 1

            # 🔥 MULTIPLE ALARMS (UNIQUE ID)
            alarm_id = f"TEMP_HIGH_{time.time()}"

            ctx.alarm_manager.trigger(
                alarm_id,
                "High temperature detected",
                priority="HIGH"
            )

            msg = "HIGH TEMPERATURE DETECTED"

            if ctx.kpi.warning_count >= config["warning_limit"]:
                msg = "WARNING: High Temperature"

            if ctx.kpi.error_count >= config["error_limit"]:
                ctx.error.lock()

            return {"state": "ERROR", "message": msg}

        return {"state": "NORMAL", "message": ""}