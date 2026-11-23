# You should define the values of:
# the client id (line 14)
# the broker (line 17)
# the topic (line 21)

from paho.mqtt import client as mqtt_client
import time

def cup(com):
    print(com, flush=True)

cup('getid')
id = input()
client_id = '***id****'+id

# Broker
broker = '***broker***'
port = 1883

# Topic
topic = '***topic***'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            cup('print Connected!')
        else:
            cup('print Failed to connect!')

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
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
    client.loop_start()
    publish(client)
    client.loop_stop()


if __name__ == '__main__':
    run()