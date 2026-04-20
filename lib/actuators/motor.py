from .base_actuator import BaseActuator

class Motor(BaseActuator):
    def __init__(self, name="Motor"):
        super().__init__(name)