class KPI:
    def __init__(self):
        self.run_time = 0
        self.stop_time = 0
        self.item_count = 0
        self.accepted = 0
        self.rejected = 0
        self.last_item = False

    def update(self, state, item_detected):
        if state == "RUN":
            self.run_time += 1
        else:
            self.stop_time += 1

        if item_detected and not self.last_item:
            self.item_count += 1
            if state == "RUN":
                self.accepted += 1
            else:
                self.rejected += 1

        self.last_item = item_detected

    def efficiency(self):
        total = self.run_time + self.stop_time
        return (self.run_time / total * 100) if total else 0