class Controller:

    def __init__(self, motor, conveyor, alarm):
        self.motor = motor
        self.conveyor = conveyor
        self.alarm = alarm

    def update(self, state, item_detected):

        # [INVALID] FULL STOP ONLY HERE
        if state == "LOCKED":
            self.motor.stop()
            self.conveyor.stop()
            self.alarm.activate()
            return

        #  ALWAYS RUN
        self.conveyor.start()
        self.alarm.deactivate()

        if item_detected:
            self.motor.start()
        else:
            self.motor.stop()