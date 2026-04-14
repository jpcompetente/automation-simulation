from devices.base.sensor_base import BaseSensor
import random

class VibrationSensor(BaseSensor):

    def read(self, state=None):
        if state == "RUN":
            return random.randint(3, 10)
        return random.randint(0, 2)