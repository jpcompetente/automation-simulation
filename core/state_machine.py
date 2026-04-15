class StateMachine:
    IDLE = "IDLE"
    RUN = "RUN"
    ERROR = "ERROR"
    STOP = "STOP"

    def __init__(self):
        self.state = self.IDLE  # Set the initial state to IDLE

    def get_state(self):
        """Returns the current state of the machine"""
        return self.state

    def transition(self, command, temperature=None):
        # If the system is in ERROR state, handle reset command
        if self.state == self.ERROR:
            if command == "RESET":
                self.state = self.IDLE
            return self.state

        # If the temperature exceeds the threshold, set state to ERROR
        if temperature is not None and temperature > 60:
            self.state = self.ERROR
            return self.state

        # Handle normal commands
        if command == "START":
            self.state = self.RUN
        elif command == "STOP":
            self.state = self.STOP
        elif command == "RESET":
            self.state = self.IDLE

        return self.state