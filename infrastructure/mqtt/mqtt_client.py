import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port, topic_sub, topic_pub):
        # Initialize MQTT client, setting broker, port, and topics
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub

        # Initialize callback functions for connect and message
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        """
        Called when the client connects to the broker.
        """
        print(f"Connected to broker with result code {rc}")
        client.subscribe(self.topic_sub)  # Subscribe to the topic when connected

    def on_message(self, client, userdata, msg):
        """
        Called when a message is received on the subscribed topic.
        """
        try:
            payload = msg.payload.decode()  # Decode the message payload
            print(f"Message received: {payload}")
        except Exception as e:
            print(f"Error decoding message: {e}")

    def send_message(self, message):
        """
        Send a message to the publisher topic.
        """
        try:
            self.client.publish(self.topic_pub, message)
            print(f"Message sent: {message}")
        except Exception as e:
            print(f"Error sending message: {e}")

    def start(self):
        """
        Connect to the broker and start the loop to listen for messages.
        """
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()  # Start the loop to listen for incoming messages
        except Exception as e:
            print(f"Error connecting to broker: {e}")

    def stop(self):
        """
        Stop the MQTT client loop.
        """
        self.client.loop_stop()
        print("MQTT loop stopped")