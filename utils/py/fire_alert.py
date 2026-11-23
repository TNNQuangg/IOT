# fire_alert.py — CupCarbon IoT node script
# When the node becomes marked, it publishes the id of the publishing
# node on the topic cupcarbon/fire of the HiveMQ public broker.
# Requires on the machine: pip install paho-mqtt

from cup_functions import *
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT   = 1883
TOPIC  = "cupcarbon/fire"

node_id = cup_getid()                      # id of this node

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                     client_id="cup_fire_node_" + str(node_id))
client.connect(BROKER, PORT, keepalive=30)
client.loop_start()

was_marked = False
while True:
    marked = cup_ismarked()
    if marked and not was_marked:          # publish once per marking
        client.publish(TOPIC, str(node_id), qos=1)
        cup_print("fire alert sent by node", node_id)
    was_marked = marked
    cup_wait(0.5)
