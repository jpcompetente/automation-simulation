from lib.actuators.conveyor import Conveyor as ConveyorLib

class Conveyor:
    def __init__(self):
        self.conveyor = ConveyorLib()

    def start(self):
        self.conveyor.start()

    def stop(self):
        self.conveyor.stop()

    def status(self):
        return self.conveyor.status()