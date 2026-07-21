class Controller:
    def __init__(self, motor, conveyor, alarm):
        self.motor = motor
        self.conveyor = conveyor
        self.alarm = alarm

    def update(self, state, item_detected):
        if state == "RUN":
            self.conveyor.start()
            self.alarm.deactivate()
            if item_detected:
                self.motor.start()
            else:
                self.motor.stop()
        else:
            # IDLE, STOP, or any non-RUN state
            self.conveyor.stop()
            self.motor.stop()
            self.alarm.deactivate()
