import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, broker, port, topic_sub, topic_pub):
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        # Auto-reconnect: start at 1s delay, back off up to 30s between retries
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to broker with result code {rc}")
            client.subscribe(self.topic_sub)
        else:
            print(f"Failed to connect to broker, result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"Unexpected disconnect from broker (code {rc}), attempting to reconnect...")
        else:
            print("Disconnected from broker")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            print(f"Message received: {payload}")
        except Exception as e:
            print(f"Error decoding message: {e}")

    def send_message(self, message):
        try:
            result = self.client.publish(self.topic_pub, message)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"Publish failed (not connected?), rc={result.rc}")
            else:
                print(f"Message sent: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")

    def start(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Error connecting to broker: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT loop stopped")
