import time, random
import paho.mqtt.client as mqtt

# MQTT Broker (free test broker by Eclipse Mosquitto)
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "myhome/room1/temperature"

# Create MQTT client
client = mqtt.Client()

# Connect to broker
client.connect(BROKER, PORT, 60)
print("Connected to MQTT broker")

# Publish random sensor values every 2 seconds
try:
    while True:
        temperature = round(random.uniform(20.0, 30.0), 2)  # Fake temperature
        humidity = round(random.uniform(40.0, 70.0), 2)     # Fake humidity

        payload = f'{{"temperature": {temperature}, "humidity": {humidity}}}'
        client.publish(TOPIC, payload)
        print(f"Sent: {payload}")
        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped publishing")
    client.disconnect()