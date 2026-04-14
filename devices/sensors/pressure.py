from devices.base.sensor_base import BaseSensor
import random

class PressureSensor(BaseSensor):

    def read(self, state=None):
        if state == "RUN":
            return random.randint(70, 120)
        return random.randint(30, 60)