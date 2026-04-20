class DigitalSensor:
    def __init__(self, name):
        self.name = name
        self.state = False

    def read(self, system_state=None):
        import random
        self.state = random.choice([True, False])
        return self.state