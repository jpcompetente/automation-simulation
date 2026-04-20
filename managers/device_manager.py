class DeviceManager:

    def __init__(self):
        self.sensors = {}
        self.actuators = {}

    # ---------- SENSORS ----------
    def add_sensor(self, name, sensor):
        self.sensors[name] = sensor

    def get_sensor(self, name):
        return self.sensors.get(name)

    # ---------- ACTUATORS ----------
    def add_actuator(self, name, actuator):
        self.actuators[name] = actuator

    def get_actuator(self, name):
        return self.actuators.get(name)