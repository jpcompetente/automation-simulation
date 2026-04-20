class StateLogger:
    def __init__(self):
        self.history = []

    def log(self, state):
        self.history.append(state)

    def last(self):
        return self.history[-1] if self.history else None

    def all(self):
        return self.history