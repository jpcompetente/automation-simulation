class Motor:
    def __init__(self):
        self._status = False

    def activate(self):
        self._status = True
        print("[REAL] Motor ON")

    def deactivate(self):
        self._status = False
        print("[REAL] Motor OFF")

    def status(self):
        return self._status