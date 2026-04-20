import random
from .base_sensor import BaseSensor

class ProximitySensor(BaseSensor):
    def detect(self, state=None):
        if state == "RUN":
            return random.choice([True, False, False])
        return False