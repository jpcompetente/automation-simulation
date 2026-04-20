class EventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event, callback):
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(callback)

    def publish(self, event, data=None):
        for callback in self.subscribers.get(event, []):
            callback(data)