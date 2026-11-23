# You should define the values of:
# the client id (line 14)
# the broker (line 17)
# the topic (line 21)

from paho.mqtt import client as mqtt_client


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

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        message = msg.payload.decode()
        if message=='1':
            cup('print RECEIVED 1')
            cup('mark')
        if message=='0':
            cup('print RECEIVED 0')
            cup('unmark')

    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()