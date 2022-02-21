from ipaddress import ip_address
import smbus2
import json
import time
import paho.mqtt.client as mqtt


from temp_and_humidity import get_humidity, get_temp
from light import get_light_data
from serial import getserial

bus = smbus2.SMBus(1)

reading = False

broker_address = "3.145.141.152"
conditions_topic = "IC.embedded/cdc/conditions"


def read_and_send_data():
    """
    obtains data from sensors and sends it to broker
    """
    global count
    print(f"count: {count}")

    temp = get_temp(bus)
    humidity = get_humidity(bus)
    light_data = get_light_data(bus)

    sensor_data = {
        "serial_number": serial_number,
        "count": count,
        "temp": temp,
        "humidity": humidity,
        "light_data": light_data,
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
client.username_pw_set(username="sammy", password="raspberry")
client.connect(broker_address)

while True:

    if reading != False:
        read_and_send_data()

    else:
        print("nothing to see")

    client.loop(0.1)

    time.sleep(5)
