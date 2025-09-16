import streamlit as st
import paho.mqtt.client as mqtt
import json
import pandas as pd
import time

# MQTT Settings
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "myhome/room1/temperature"

# Global dataframe to store sensor data
data = pd.DataFrame(columns=["time", "temperature", "humidity"])

# MQTT Callback
def on_message(client, userdata, msg):
    global data
    try:
        payload = json.loads(msg.payload.decode())
        temp = payload.get("temperature", None)
        hum = payload.get("humidity", None)
        if temp is not None and hum is not None:
            new_row = {"time": time.strftime("%H:%M:%S"), 
                       "temperature": temp, 
                       "humidity": hum}
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
    except Exception as e:
        print("Error:", e)

# MQTT Setup
client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)
client.loop_start()

# Streamlit UI
st.title("🌡️ IoT Dashboard - Temperature & Humidity")
st.write("Real-time data from fake IoT sensor via MQTT")

placeholder = st.empty()

while True:
    with placeholder.container():
        if not data.empty:
            st.line_chart(data.set_index("time")[["temperature", "humidity"]])
            st.table(data.tail(5))
    time.sleep(2)
