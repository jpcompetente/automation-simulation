class KPIManager:
    def __init__(self):
        self.run_time = 0
        self.stop_time = 0
        self.item_count = 0
        self.accepted_count = 0
        self.rejected_count = 0
        self.error_count = 0
        self.warning_count = 0

        self.last_item = False

    def reset(self):
        self.__init__()

    def update(self, state, item_detected):

        # 🔥 FIXED TIME LOGIC
        if state == "RUN":
            self.run_time += 1
        else:
            self.stop_time += 1

        # ---------- ITEM LOGIC ----------
        if item_detected and not self.last_item:
            self.item_count += 1

            if state == "RUN":
                self.accepted_count += 1
            else:
                self.rejected_count += 1

        self.last_item = item_detected

    def compute(self):
        total_time = self.run_time + self.stop_time

        rate = (self.item_count / self.run_time * 60) if self.run_time > 0 else 0
        error_percent = (self.error_count / self.item_count * 100) if self.item_count > 0 else 0
        efficiency = (self.run_time / total_time * 100) if total_time > 0 else 0
        yield_percent = (self.accepted_count / self.item_count * 100) if self.item_count > 0 else 0

        return {
            "rate": rate,
            "error_percent": error_percent,
            "efficiency": efficiency,
            "yield_percent": yield_percent
        }