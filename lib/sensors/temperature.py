import random
from .base_sensor import BaseSensor

class TemperatureSensor(BaseSensor):
    def __init__(self, name="TempSensor"):
        super().__init__(name)
        self.base_temp = 30

    def read(self, state=None):
        if state == "RUN":
            return self.base_temp + random.randint(10, 35)
        elif state == "ERROR":
            return 70 + random.randint(0, 20)
        elif state == "STOP":
            return self.base_temp + random.randint(-3, 3)
        return self.base_temp + random.randint(-2, 5)