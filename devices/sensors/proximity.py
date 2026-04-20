from lib.sensors.proximity import ProximitySensor

class ProximityDevice:
    def __init__(self):
        self.sensor = ProximitySensor()

    def detect(self, state):
        return self.sensor.detect(state)