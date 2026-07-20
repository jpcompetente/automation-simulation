class OPCUAClient:
    def __init__(self, endpoint="opc.tcp://localhost:4840"):
        self.endpoint = endpoint
        self.connected = False

    def connect(self):
        print(f"[OPCUA] Connecting to {self.endpoint}")
        self.connected = True

    def read(self, node):
        if not self.connected:
            raise Exception("OPCUA not connected")

        #  placeholder
        return None

    def write(self, node, value):
        if not self.connected:
            raise Exception("OPCUA not connected")

        print(f"[OPCUA] Write {value} to {node}")

    def disconnect(self):
        self.connected = False
        print("[OPCUA] Disconnected")