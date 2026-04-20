class StateMachineBase:
    def __init__(self, initial_state):
        self.state = initial_state
        self.transitions = {}

    def add_transition(self, from_state, condition, to_state):
        """
        condition = function(context) -> True/False
        """
        if from_state not in self.transitions:
            self.transitions[from_state] = []

        self.transitions[from_state].append((condition, to_state))

    def update(self, context):
        """
        context = dictionary (data)
        """
        if self.state not in self.transitions:
            return self.state

        for condition, new_state in self.transitions[self.state]:
            if condition(context):
                self.state = new_state
                break

        return self.state

    def get_state(self):
        return self.state

    def reset(self, state):
        self.state = state