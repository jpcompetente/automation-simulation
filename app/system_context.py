class SystemContext:
    def __init__(self):
        self.devices = None

        # sensors
        self.temp = None
        self.prox = None

        # actuators
        self.motor = None
        self.conveyor = None
        self.alarm = None

        # core
        self.state_machine = None
        self.controller = None
        self.system = None

        # services
        self.watchdog = None
        self.logger = None
        self.kpi = None
        self.error = None

        # runtime
        self.command = ""