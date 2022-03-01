import smbus2
import time
from ipaddress import ip_address
import json
import paho.mqtt.client as mqtt

from serial import getserial

#################
#### Globals ####
#################

# --- Light spectrum --- #
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

# --- Light Intensity --- #
TSLaddr = 0x39  # Default I2C address, alternate 0x29, 0x49
TSLcmd = 0x80  # Command
chan0 = 0x0C  # Read Channel0 sensor date
chan1 = 0x0E  # Read channel1 sensor data
TSLon = 0x03  # Switch sensors on
TSLoff = 0x00  # Switch sensors off
# Exposure settings
LowShort = 0x00  # x1 Gain 13.7 miliseconds
LowMed = 0x01  # x1 Gain 101 miliseconds
LowLong = 0x02  # x1 Gain 402 miliseconds
LowManual = 0x03  # x1 Gain Manual
HighShort = 0x10  # LowLight x16 Gain 13.7 miliseconds
HighMed = 0x11  # LowLight x16 Gain 100 miliseconds
HighLong = 0x12  # LowLight x16 Gain 402 miliseconds
HighManual = 0x13  # LowLight x16 Gain Manual
# Manual Settings
ManDelay = 2  # Manual Exposure in Seconds
StartMan = 0x1F  # Start Manual Exposure
EndMan = 0x1E  # End Manual Exposure

# --- MQTT --- #
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
    while readColour(CTRL_SETUP) & DATA_RDY == 0:
        time.sleep(0.1)

    # Read data
    low_v = readColour(VIOLET_LOW)
    high_v = readColour(VIOLET_HIGH)

    low_b = readColour(BLUE_LOW)
    high_b = readColour(BLUE_HIGH)

    low_g = readColour(GREEN_LOW)
    high_g = readColour(GREEN_HIGH)

    low_y = readColour(YELLOW_LOW)
    high_y = readColour(YELLOW_HIGH)

    low_o = readColour(ORANGE_LOW)
    high_o = readColour(ORANGE_HIGH)

    low_r = readColour(RED_LOW)
    high_r = readColour(RED_HIGH)

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


def get_temp() -> float:
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
def get_humidity() -> float:
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


###################
#### Intensity ####
###################

# Number of sensor readings
vRepeat = 20
try:
    # Enter in [] the Exposure Setting to use
    sequence = [HighLong] * vRepeat  # repeat reading vRepeat times for setting>
except:
    print("Unknown Exposure Setting used, defaulting to LowLong (x1 402ms")
    sequence = [LowLong] * vRepeat


def luxcalc(Result0, Result1):
    """Basic Lux Calculation value"""
    # see data sheet for lux calculation details
    # and to calculate lux correctly for all modes
    ResDiv = int(Result1) / int(Result0)
    if ResDiv > 0 and ResDiv <= 0.50:
        lux = 0.0304 * Result0 - 0.062 * Result0 * (Result1 / Result0) ** 1.4
    if ResDiv > 0.50 and ResDiv <= 0.61:
        lux = 0.0224 * Result0 - 0.031 * Result1
    if ResDiv > 0.61 and ResDiv <= 0.8:
        lux = 0.0128 * Result0 - 0.0153 * Result1
    if ResDiv > 0.8 and ResDiv <= 1.3:
        lux = 0.00146 * Result0 - 0.00112 * Result1
    if ResDiv > 1.3:
        lux = 0
    return lux


def manual(delay, mode):
    """manual exposure"""
    bus.write_byte_data(TSLaddr, 0x01 | TSLcmd, mode)  # sensativity mode
    bus.write_byte_data(TSLaddr, 0x01 | TSLcmd, StartMan)  # start detection
    time.sleep(delay)  # exposure
    bus.write_byte_data(TSLaddr, 0x01 | TSLcmd, EndMan)  # stop detection
    return


def CurTime():
    """Returns the current date and time"""
    t1 = time.asctime(time.localtime(time.time()))
    return t1


def get_intensity() -> float:
    """
    obtains and returns current light intensity reading

    :return: float of current intensity reading
    """
    output = 0
    count = 0
    writebyte = bus.write_byte_data
    # Power On
    writebyte(TSLaddr, 0x00 | TSLcmd, TSLon)

    # print("Part Number", bus.read_byte_data(TSLaddr, 0x8A))
    for item in sequence:
        if item != 3 and item != 19:  # Selected built in delay for exposure. If >
            writebyte(TSLaddr, 0x01 | TSLcmd, item)
            # Give sensor time to write results before collecting reading.
            # 13.7ms  write several readings before sleep complete, 402ms wo>
            time.sleep(0.5)
        else:  # use manual exposure
            manual(ManDelay, item)
        # Read Ch0 Word
        data = bus.read_i2c_block_data(TSLaddr, chan0 | TSLcmd, 2)
        # Read CH1 Word
        data1 = bus.read_i2c_block_data(TSLaddr, chan1 | TSLcmd, 2)
        # Convert the data to Integer
        ch0 = data[1] * 256 + data[0]
        ch1 = data1[1] * 256 + data1[0]
        # Output data to screen
        vTime = CurTime()
        if ch0 > 0:
            vLux = round(luxcalc(ch0, ch1), 5)
            # print("Lux", vLux)
            output += vLux
            count += 1
        else:
            # either no light or clipping value exceeded due to too much lig>
            print("No Light")
    # Power Off
    writebyte(TSLaddr, 0x00 | TSLcmd, TSLoff)
    if count == 0:
        output = 0
    else:
        output = output / count
    return output


##############
#### main ####
##############


def read_and_send_data():
    """
    obtains data from sensors and sends it to broker
    """
    global count
    print(f"count: {count}")

    temp = round(get_temp(), 2)
    humidity = round(get_humidity(), 2)
    light_data = get_light_data()
    intensity = round(get_intensity(), 2)

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
client.username_pw_set(username="sammy", password="raspberry")
client.connect(broker_address, port=8883)

while True:

    if reading != False:
        read_and_send_data()

    else:
        print("nothing to see")

    client.loop(0.1)

    time.sleep(5)
