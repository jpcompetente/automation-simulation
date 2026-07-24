import random
from .base_sensor import BaseSensor


class TemperatureSensor(BaseSensor):
    def __init__(self, name="TempSensor"):
        super().__init__(name)
        self.current_temp = 30.0

    def read(self, state=None):
        if state == "RUN":
            target = random.uniform(40, 65)
            step = random.uniform(0.5, 2.0)
        elif state == "ERROR":
            target = random.uniform(70, 90)
            step = random.uniform(1.0, 3.0)
        elif state == "STOP":
            target = random.uniform(28, 35)
            step = random.uniform(0.3, 1.0)
        else:
            target = random.uniform(28, 35)
            step = random.uniform(0.3, 1.0)

        # Move current_temp gradually toward target instead of jumping
        if self.current_temp < target:
            self.current_temp = min(self.current_temp + step, target)
        elif self.current_temp > target:
            self.current_temp = max(self.current_temp - step, target)

        return round(self.current_temp, 1)
