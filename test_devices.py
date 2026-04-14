from devices.sensors.temperature import TemperatureSensor
from devices.actuators.motor import Motor
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
temp = TemperatureSensor("Temp")
motor = Motor()

print("Temperature:", temp.read("RUN"))

motor.start()
print("Motor status:", motor.status())