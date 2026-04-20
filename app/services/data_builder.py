def build_payload(state, header_state, temperature, motor, conveyor, alarm,
                  item_detected, kpi, metrics, error_manager):

    return {
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

        "error_message": error_manager.message,
        "error_locked": error_manager.locked
    }