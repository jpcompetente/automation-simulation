from devices.base.sensor_base import BaseSensor
import random

class TemperatureSensor(BaseSensor):

    def read(self, state=None):
        if state == "RUN":
            return random.randint(50, 80)
        return random.randint(20, 40)