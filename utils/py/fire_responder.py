# fire_responder.py — CupCarbon IoT node script
# Subscribes to cupcarbon/fire (HiveMQ). When a message arrives — the id
# of the node that raised the alert (see fire_alert.py) — this node
# computes a road route to that node (cup_route) and drives to it
# (cup_routego). Requires: pip install paho-mqtt, and internet access
# (the route is computed by the web routing API).

from cup_functions import *
import queue
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT   = 1883
TOPIC  = "cupcarbon/fire"

node_id = cup_getid()                      # id of this responder node
alerts = queue.Queue()                     # fire ids received by MQTT

def on_message(client, userdata, msg):
    try:
        alerts.put(int(msg.payload.decode().strip()))
    except ValueError:
        pass                               # ignore non-numeric payloads

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                     client_id="cup_fire_responder_" + str(node_id))
client.on_message = on_message
client.connect(BROKER, PORT, keepalive=30)
client.subscribe(TOPIC, qos=1)
client.loop_start()

cup_print("responder", node_id, "ready")

while True:
    try:
        fire_id = alerts.get(timeout=0.5)  # wait for an alert
    except queue.Empty:
        cup_wait(0.1)                      # keep the simulation protocol alive
        continue
    if fire_id == node_id:                 # my own alert: ignore it
        continue
    cup_print("fire at node", fire_id, "- on my way")
    cup_route(node_id, fire_id)            # road route me -> alerting node
    cup_routego()                          # drive there
