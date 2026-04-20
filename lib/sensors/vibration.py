import random
from .base_sensor import BaseSensor

class VibrationSensor(BaseSensor):
    def __init__(self, name="Vibration"):
        super().__init__(name)

    def read(self, state=None):
        if state == "RUN":
            return random.randint(3, 10)
        elif state == "ERROR":
            return random.randint(8, 15)
        return random.randint(0, 2)