import time

class Watchdog:
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.last_feed = time.time()

    def feed(self):
        self.last_feed = time.time()

    def is_alive(self):
        return (time.time() - self.last_feed) < self.timeout