class TemperatureSensor:
    def __init__(self, name):
        self.name = name
        self.temp = 30

    def read(self, state=None):
        # simulate realistic behavior
        if state == "RUN":
            self.temp += 0.5
        elif state == "ERROR":
            self.temp += 1

        # clamp values
        if self.temp > 100:
            self.temp = 100

        return self.temp