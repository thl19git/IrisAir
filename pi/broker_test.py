from ipaddress import ip_address
import json
import time
import paho.mqtt.client as mqtt

reading = False

broker_address = "3.145.141.152"
general_broker_address = "broker.mqttdashboard.com"
conditions_topic = "IC.embedded/cdc/conditions"
test_topic = "test"


def getserial() -> str:
    """
    Obtains serial number of raspbery pi

    :return: string of serial number or error
    """
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open("/proc/cpuinfo", "r")
        for line in f:
            if line[0:6] == "Serial":
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"

    return cpuserial


def send_data():
    global count
    print(f"count: {count}")

    sensor_data = {
        "serial_number": serial_number,
        "count": count,
        "temp": count * 23,
        "humidity": float(count / 1.5),
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
    client.publish(test_topic, "can you see mee")

    if reading != False:
        send_data()

    else:
        print("nothing to see")

    client.loop(0.1)

    time.sleep(5)
