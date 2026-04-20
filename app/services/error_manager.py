class ErrorManager:
    def __init__(self):
        self.locked = False
        self.message = ""
        self.last_logged = ""

    def set_error(self, msg, logger=None):
        self.message = msg

        if logger and msg != self.last_logged:
            logger.log(msg)
            self.last_logged = msg

    def lock(self):
        self.locked = True
        self.message = "LOCKED - 100 Errors Reached"

    def reset(self):
        self.locked = False
        self.message = ""
        self.last_logged = ""

    def clear(self):
        self.message = ""