from devices.base.actuator_base import BaseActuator

class Valve(BaseActuator):

    def __init__(self):
        super().__init__("Valve")

    def open(self):
        self.start()

    def close(self):
        self.stop()