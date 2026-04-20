from lib.actuators.motor import Motor as MotorLib

class Motor:
    def __init__(self):
        self.motor = MotorLib()

    def start(self):
        self.motor.start()

    def stop(self):
        self.motor.stop()

    def status(self):
        return self.motor.status()