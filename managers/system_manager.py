class SystemManager:
    def __init__(self, state_machine, controller):
        self.sm = state_machine
        self.controller = controller

    def process(self, command, temperature, item_detected, high_threshold=60):
        #  STATE TRANSITION
        state = self.sm.transition(command, temperature, high_threshold)
        self.sm.state = state

        #  CONTROL DEVICES
        self.controller.update(state, item_detected)

        return state
