from devices.base.actuator_base import BaseActuator

class Conveyor(BaseActuator):

    def __init__(self):
        super().__init__("Conveyor")

    def start(self):
        self._status = True
        print("Conveyor STARTED")

    def stop(self):
        self._status = False
        print("Conveyor STOPPED")