# CupCarbon MQTT publisher node
# Compatible with Python 3.14 and paho-mqtt 2.x
#
# You should define the values of:
# the client id prefix (line 19)
# the broker (line 24)
# the topic (line 28)

from paho.mqtt import client as mqtt_client
import time

def cup(com):
    print(com, flush=True)

cup('getid')
node_id = input()

# Client ID
client_id = '***id***' + node_id

# Broker
# broker = 'broker.hivemq.com'
# broker = 'broker.emqx.io'
broker = '***broker***'
port = 1883

# Topic
topic = '***topic***'

def on_connect(client, userdata, flags, reason_code, properties):
    # paho-mqtt 2.x callback signature (CallbackAPIVersion.VERSION2)
    if reason_code == 0:
        cup('print Connected!')
    else:
        cup(f'print Failed to connect! ({reason_code})')

def connect_mqtt():
    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION2,
        client_id=client_id
    )
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
    while True:
        client.publish(topic, '1')
        cup('print SEND 1')
        time.sleep(1)
        client.publish(topic, '0')
        cup('print SEND 0')
        time.sleep(1)

def run():
    client = connect_mqtt()
    client.loop_start()          # network loop runs in a background thread
    try:
        publish(client)
    finally:                     # clean shutdown when the node is stopped
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    run()
