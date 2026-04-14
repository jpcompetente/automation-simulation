from datetime import datetime

class Logger:

    @staticmethod
    def log(data):
        time_now = datetime.now().strftime("%H:%M:%S")
        print(f"[{time_now}] {data}")