class Alarm:
    def __init__(self):
        self.active = False

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def status(self):
        return self.active