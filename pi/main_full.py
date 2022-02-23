import smbus2
import time
from ipaddress import ip_address
import json
import paho.mqtt.client as mqtt

from serial import getserial

#################
#### Globals ####
#################

AS726X_SLAVE_STATUS_REG = 0x00
AS726X_SLAVE_WRITE_REG = 0x01
AS726X_SLAVE_READ_REG = 0x02

AS726X_SLAVE_TX_VALID = 0x02
AS726X_SLAVE_RX_VALID = 0x01

DATA_RDY = 0x02

HW_VERSION_LOW = 0x00
CTRL_SETUP = 0x04
INT_T = 0x05
VIOLET_HIGH = 0x08
VIOLET_LOW = 0x09
BLUE_HIGH = 0x0A
BLUE_LOW = 0x0B
GREEN_HIGH = 0x0C
GREEN_LOW = 0x0D
YELLOW_HIGH = 0x0E
YELLOW_LOW = 0x0F
ORANGE_HIGH = 0x10
ORANGE_LOW = 0x11
RED_HIGH = 0x12
RED_LOW = 0x13

VIOLET_CALIBRATED = 0x14
BLUE_CALIBRATED = 0x18
GREEN_CALIBRATED = 0x1C
YELLOW_CALIBRATED = 0x20
ORANGE_CALIBRATED = 0x24
RED_CALIBRATED = 0x28

broker_address = "3.145.141.152"
conditions_topic = "IC.embedded/cdc/conditions"

#####################
#### Initilising ####
#####################
bus = smbus2.SMBus(1)

reading = False

####################
#### Light data ####
####################


def writeVReg(addr, data):
    """
    writes to virtal register

    :param addr: address of virtual register

    :param data: data to be sent to virtual register

    :param bus: smbus class
    """

    while True:
        write = smbus2.i2c_msg.write(0x49, [AS726X_SLAVE_STATUS_REG])
        read = smbus2.i2c_msg.read(0x49, 1)
        bus.i2c_rdwr(write, read)
        status = int.from_bytes(read.buf[0], "big")
        if (status & AS726X_SLAVE_TX_VALID) == 0:
            break

    write = smbus2.i2c_msg.write(0x49, [AS726X_SLAVE_WRITE_REG, addr | 0x80])
    bus.i2c_rdwr(write)

    while True:
        write = smbus2.i2c_msg.write(0x49, [AS726X_SLAVE_STATUS_REG])
        read = smbus2.i2c_msg.read(0x49, 1)
        bus.i2c_rdwr(write, read)
        status = int.from_bytes(read.buf[0], "big")
        if (status & AS726X_SLAVE_TX_VALID) == 0:
            break

    write = smbus2.i2c_msg.write(0x49, [AS726X_SLAVE_WRITE_REG, data])
    bus.i2c_rdwr(write)


def readColour(addr) -> int:
    """
    Reads from a virtual register

    :param addr: address of virtual register

    :param bus: smbus class

    :return: data in virtual register
    """

    while True:
        write = smbus2.i2c_msg.write(0x49, [AS726X_SLAVE_STATUS_REG])
        read = smbus2.i2c_msg.read(0x49, 1)
        bus.i2c_rdwr(write, read)
        status = int.from_bytes(read.buf[0], "big")
        if (status & AS726X_SLAVE_TX_VALID) == 0:
            break

    write = smbus2.i2c_msg.write(0x49, [AS726X_SLAVE_WRITE_REG, addr])
    bus.i2c_rdwr(write)

    while True:
        write = smbus2.i2c_msg.write(0x49, [AS726X_SLAVE_STATUS_REG])
        read = smbus2.i2c_msg.read(0x49, 1)
        bus.i2c_rdwr(write, read)
        status = int.from_bytes(read.buf[0], "big")
        if (status & AS726X_SLAVE_RX_VALID) != 0:
            break

    write = smbus2.i2c_msg.write(0x49, [AS726X_SLAVE_READ_REG])  # Select phys. r>
    read = smbus2.i2c_msg.read(0x49, 1)  # Read 1 byte
    bus.i2c_rdwr(write, read)

    return int.from_bytes(read.buf[0], "big")


writeVReg(INT_T, 0xFF)  # Set integration time
writeVReg(CTRL_SETUP, 0x38)  # Set gain and bank (sample mode). 0x38 = max gain,


def get_light_data():
    """
    returns dictonary containing values for all colors

    :return: dictionary with all colors
    """

    # Wait for data valid
    while readColour(CTRL_SETUP, bus) & DATA_RDY == 0:
        time.sleep(0.1)

    # Read data
    low_v = readColour(VIOLET_LOW, bus)
    high_v = readColour(VIOLET_HIGH, bus)

    low_b = readColour(BLUE_LOW, bus)
    high_b = readColour(BLUE_HIGH, bus)

    low_g = readColour(GREEN_LOW, bus)
    high_g = readColour(GREEN_HIGH, bus)

    low_y = readColour(YELLOW_LOW, bus)
    high_y = readColour(YELLOW_HIGH, bus)

    low_o = readColour(ORANGE_LOW, bus)
    high_o = readColour(ORANGE_HIGH, bus)

    low_r = readColour(RED_LOW, bus)
    high_r = readColour(RED_HIGH, bus)

    violet = high_v * 256 + low_v
    blue = high_b * 256 + low_b
    green = high_g * 256 + low_g
    yellow = high_y * 256 + low_y
    orange = high_o * 256 + low_o
    red = high_r * 256 + low_r

    light_data = {
        "violet": violet,
        "blue": blue,
        "green": green,
        "yellow": yellow,
        "orange": orange,
        "red": red,
    }

    # print(light_data)

    return light_data


##############
#### Temp ####
##############


def get_temp(bus) -> float:
    """
    obtains and returns current tempriture reading

    :return: float of current tempriture reading
    """

    meas_temp = smbus2.i2c_msg.write(0x40, [0xF3])

    bus.i2c_rdwr(meas_temp)

    time.sleep(0.1)

    read_result = smbus2.i2c_msg.read(0x40, 2)
    bus.i2c_rdwr(read_result)

    temp = int.from_bytes(read_result.buf[0] + read_result.buf[1], "big")

    temp_final = 175.72 * temp / 65536 - 46.85

    return temp_final


##################
#### Humidity ####
##################
def get_humidity(bus) -> float:
    """
    obtains and returns current humidity reading

    :return: float of current humidity reading
    """

    meas_humid = smbus2.i2c_msg.write(0x40, [0xF5])

    bus.i2c_rdwr(meas_humid)
    time.sleep(0.1)

    read_result = smbus2.i2c_msg.read(0x40, 2)
    bus.i2c_rdwr(read_result)

    humid = int.from_bytes(read_result.buf[0] + read_result.buf[1], "big")
    humid_final = 125 * humid / 65536 - 6

    return humid_final


##############
#### main ####
##############


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
