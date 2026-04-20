class DecisionEngine:
    def decide(self, context):
        """
        context = {
            "temperature": int,
            "item_detected": bool,
            "error": bool
        }
        """
        if context.get("error"):
            return "STOP"

        if context.get("temperature", 0) > 80:
            return "WARNING"

        if context.get("item_detected"):
            return "RUN"

        return "IDLE"