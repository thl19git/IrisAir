import smbus2
import time


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
