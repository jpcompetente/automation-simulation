from lib.actuators.alarm import Alarm as AlarmLib

class Alarm:
    def __init__(self):
        self.alarm = AlarmLib()

    def activate(self):
        self.alarm.activate()

    def deactivate(self):
        self.alarm.deactivate()

    def status(self):
        return self.alarm.status()