import random
from .base_sensor import BaseSensor

class PressureSensor(BaseSensor):
    def __init__(self, name="Pressure"):
        super().__init__(name)

    def read(self, state=None):
        if state == "RUN":
            return random.randint(70, 120)
        elif state == "ERROR":
            return random.randint(100, 150)
        return random.randint(30, 60)