from devices.base.sensor_base import BaseSensor
import random

class ProximitySensor(BaseSensor):

    def detect(self, state=None):
        if state == "RUN":
            return random.choice([True, False])
        return False