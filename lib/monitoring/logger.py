from datetime import datetime

class Logger:
    def __init__(self, filename=None):
        self.filename = filename

    def log(self, message):
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{time_now}] {message}"

        if self.filename:
            with open(self.filename, "a") as f:
                f.write(log_msg + "\n")
        else:
            print(log_msg)