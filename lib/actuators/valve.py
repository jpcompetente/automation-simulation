from .base_actuator import BaseActuator

class Valve(BaseActuator):
    def open(self):
        self.start()

    def close(self):
        self.stop()