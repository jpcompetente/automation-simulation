class SystemManager:
    def __init__(self, state_machine, controller):
        self.sm = state_machine
        self.controller = controller

    def process(self, command, temperature, item_detected):
        # 🔥 STATE TRANSITION
        state = self.sm.transition(command, temperature)
        self.sm.state = state

        # 🔥 CONTROL DEVICES
        self.controller.update(state, item_detected)

        return state