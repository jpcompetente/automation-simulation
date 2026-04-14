class BaseActuator:
    def __init__(self, name):
        self.name = name
        self._status = False

    def start(self):
        self._status = True

    def stop(self):
        self._status = False

    def status(self):
        return self._status