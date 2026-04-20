class AlarmManager:
    def __init__(self):
        self.active_alarms = set()

    def trigger(self, message):
        self.active_alarms.add(message)

    def clear(self, message=None):
        if message:
            self.active_alarms.discard(message)
        else:
            self.active_alarms.clear()

    def has_active(self):
        return len(self.active_alarms) > 0

    def get_all(self):
        return list(self.active_alarms)