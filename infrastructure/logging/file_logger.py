from datetime import datetime

class FileLogger:
    def __init__(self, filename="system.log"):
        self.filename = filename

    def log(self, message):
        with open(self.filename, "a") as f:
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{time}] {message}\n")