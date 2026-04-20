class DigitalActuator:
    def __init__(self, name):
        self.name = name
        self._status = False

    def activate(self):
        self._status = True

    def deactivate(self):
        self._status = False

    def status(self):
        return self._status