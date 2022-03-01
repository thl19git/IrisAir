import smbus2
import time
from ipaddress import ip_address
import json
import paho.mqtt.client as mqtt
from random import uniform

from serial import getserial

#################
#### Globals ####
#################

# --- MQTT --- #
broker_address = "3.145.141.152"
conditions_topic = "IC.embedded/cdc/conditions"

#####################
#### Initilising ####
#####################

reading = False


##############
#### main ####
##############


def read_and_send_data():
    """
    obtains data from sensors and sends it to broker
    """
    global count
    print(f"count: {count}")

    temp = round(uniform(17, 27))
    humidity = round(uniform(17, 27))
    intensity = round(uniform(0, 5000))

    light_data = {
        "violet": uniform(0, 500),
        "blue": uniform(0, 500),
        "green": uniform(0, 500),
        "yellow": uniform(0, 500),
        "orange": uniform(0, 500),
        "red": uniform(0, 500),
    }

    sensor_data = {
        "serial_number": serial_number,
        "count": count,
        "temp": temp,
        "humidity": humidity,
        "light_data": light_data,
        "intensity": intensity,
    }

    json_object = json.dumps(sensor_data)

    print(json_object)

    client.publish(conditions_topic, json_object)

    count += 1
    return


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK Returned code=", rc)
    else:
        print("Bad connection Returned code=", rc)

    print(f"Connected with result code {0}")
    client.subscribe(topic)
    print("subscribed to:", topic)
    print("stage0: subscribed")


def on_message(client, userdata, message):
    global reading
    msg = message.payload.decode()

    if msg == "start":
        print("start")
        reading = True

    else:
        print("stop")
        reading = False


serial_number = getserial()
topic = f"IC.embedded/cdc/{serial_number}"

count = 0

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.tls_set(
    ca_certs="../certs/ca/ca.crt",
    certfile="../certs/client/client.crt",
    keyfile="../certs/client/client.key",
)
client.tls_insecure_set(True)
client.username_pw_set(username="sammy", password="raspberry")
client.connect(broker_address, port=8883)

while True:

    if reading != False:
        read_and_send_data()

    else:
        print("nothing to see")

    client.loop(0.1)

    time.sleep(5)
