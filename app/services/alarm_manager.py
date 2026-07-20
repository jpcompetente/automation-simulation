from datetime import datetime


class AlarmManager:

    def __init__(self):
        self.active = []
        self.history = []

    # 🔥 ADD NEW ALARM (NO DUPLICATE CHECK = MULTIPLE EVENTS)
    def trigger(self, alarm_id, message, priority="LOW"):
        for alarm in self.active:
            if alarm["id"] == alarm_id:
                return

        alarm = {
            "id": alarm_id,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ack": False
        }

        self.active.append(alarm)

    # 🔥 ACK ALL → MOVE TO HISTORY
    def acknowledge_all(self):

        for alarm in self.active:
            alarm["ack"] = True
            self.history.append(alarm)

        self.active.clear()

    # 🔥 GET ACTIVE
    def get_active(self):
        return self.active

    # 🔥 GET HISTORY
    def get_history(self):
        return self.history

    # 🔥 RESET SYSTEM
    def clear_all(self):
        self.active.clear()
        self.history.clear()
