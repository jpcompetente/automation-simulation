class BaseSensor:
    def __init__(self, name="Sensor"):
        self.name = name

    def read(self, state=None):
        raise NotImplementedError