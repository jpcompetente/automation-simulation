from devices.base.actuator_base import BaseActuator

class Motor(BaseActuator):

    def __init__(self):
        super().__init__("Motor")