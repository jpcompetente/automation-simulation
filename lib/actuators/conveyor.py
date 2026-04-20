from .base_actuator import BaseActuator

class Conveyor(BaseActuator):
    def __init__(self, name="Conveyor"):
        super().__init__(name)