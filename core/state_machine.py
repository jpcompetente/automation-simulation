class StateMachine:
    IDLE = "IDLE"
    RUN = "RUN"
    ERROR = "ERROR"
    STOP = "STOP"

    def __init__(self):
        self.state = self.IDLE

    def get_state(self):
        return self.state

    def transition(self, command, temperature=None):

        # 🔥 GLOBAL RESET (works in ANY state)
        if command == "RESET":
            self.state = self.IDLE
            return self.state

        # 🔴 ERROR STATE LOCK
        if self.state == self.ERROR:
            return self.state

        # 🌡 TEMPERATURE ERROR
        if temperature is not None and temperature > 60:
            self.state = self.ERROR
            return self.state

        # ▶ NORMAL TRANSITIONS
        if command == "START":
            self.state = self.RUN

        elif command == "STOP":
            self.state = self.STOP

        return self.state