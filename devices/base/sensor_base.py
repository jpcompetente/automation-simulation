class BaseSensor:
    def __init__(self, name):
        self.name = name

    def read(self, state=None):
        raise NotImplementedError("Sensor read() not implemented")