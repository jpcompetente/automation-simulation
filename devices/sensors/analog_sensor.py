class AnalogSensor:
    def __init__(self, name, min_val=0, max_val=100):
        self.name = name
        self.value = min_val
        self.min = min_val
        self.max = max_val

    def read(self, state=None):
        import random
        self.value += random.uniform(-1, 2)

        if self.value < self.min:
            self.value = self.min
        if self.value > self.max:
            self.value = self.max

        return round(self.value, 2)