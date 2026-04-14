from devices.base.actuator_base import BaseActuator

class Alarm(BaseActuator):

    def __init__(self):
        super().__init__("Alarm")

    def activate(self):
        self._status = True
        print("🚨 ALARM ON")

    def deactivate(self):
        self._status = False
        print("Alarm OFF")