import smbus2
import time


n = 0

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


def writeVReg(addr, data, bus):
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


def readColour(addr, bus) -> int:
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


def get_light_data(bus):
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
