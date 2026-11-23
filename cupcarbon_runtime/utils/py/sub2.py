# CupCarbon MQTT subscriber node
# Compatible with Python 3.14 and paho-mqtt 2.x
#
# You should define the values of:
# the client id prefix (line 18)
# the broker (line 24)
# the topic (line 28)

from paho.mqtt import client as mqtt_client

def cup(com):
    print(com, flush=True)

cup('getid')
node_id = input()

# Client ID
client_id = '***id***' + node_id
print(client_id, flush=True)

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
        # Subscribing here restores the subscription after any reconnection
        client.subscribe(topic)
    else:
        cup(f'print Failed to connect! ({reason_code})')

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    if message == '1':
        cup('print RECEIVED 1')
        cup('mark')
    elif message == '0':
        cup('print RECEIVED 0')
        cup('unmark')

def connect_mqtt():
    client = mqtt_client.Client(
        mqtt_client.CallbackAPIVersion.VERSION2,
        client_id=client_id
    )
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    return client

def run():
    client = connect_mqtt()
    client.loop_forever()

if __name__ == '__main__':
    run()
