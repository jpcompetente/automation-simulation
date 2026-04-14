class StateMachine:

    IDLE = "IDLE"
    RUN = "RUN"
    ERROR = "ERROR"
    STOP = "STOP"

    def __init__(self):
        self.state = self.IDLE

    def transition(self, command, temperature=None):

        # 🔥 AUTO ERROR BASED ON TEMP
        if temperature is not None and temperature > 60:
            self.state = self.ERROR
            return self.state

        # NORMAL COMMANDS
        if command == "START":
            self.state = self.RUN

        elif command == "STOP":
            self.state = self.STOP

        elif command == "RESET":
            self.state = self.IDLE

        elif command == "ERROR":
            self.state = self.ERROR

        return self.state

    def get_state(self):
        return self.state