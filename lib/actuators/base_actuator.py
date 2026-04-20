class BaseActuator:
    def __init__(self, name="Actuator"):
        self.name = name
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def status(self):
        return self._running