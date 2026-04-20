from lib.sensors.temperature import TemperatureSensor

class TempSensor:
    def __init__(self):
        self.sensor = TemperatureSensor()

    def read(self, state):
        return self.sensor.read(state)