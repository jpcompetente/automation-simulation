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

        elif state == "ERROR":
            self.motor.stop()
            self.conveyor.stop()
            self.alarm.activate()

        else:
            self.motor.stop()
            self.conveyor.stop()
            self.alarm.deactivate()