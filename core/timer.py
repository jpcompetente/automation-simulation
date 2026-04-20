import time

class Timer:
    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def elapsed(self):
        if self.start_time:
            return time.time() - self.start_time
        return 0

    def reset(self):
        self.start_time = None