class StateLogger:
    def __init__(self):
        self.history = []

    def log(self, state):
        self.history.append(state)

    def get_history(self):
        return self.history