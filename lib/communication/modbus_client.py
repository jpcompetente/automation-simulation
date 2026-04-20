class ModbusClient:
    def __init__(self, host="127.0.0.1", port=502):
        self.host = host
        self.port = port
        self.connected = False

    def connect(self):
        print(f"[Modbus] Connecting to {self.host}:{self.port}")
        self.connected = True

    def read_register(self, address):
        if not self.connected:
            raise Exception("Modbus not connected")

        # 🔥 placeholder (simulate)
        return 0

    def write_register(self, address, value):
        if not self.connected:
            raise Exception("Modbus not connected")

        print(f"[Modbus] Write {value} to {address}")

    def disconnect(self):
        self.connected = False
        print("[Modbus] Disconnected")