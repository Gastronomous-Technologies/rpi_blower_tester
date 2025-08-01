from .config import conf
from .thermal_monitor import ThermalMonitor
from time import time

def __fw_version_valid():
    return ThermalMonitor.packet.fw_version_major > 0

def do_spi_ack():
    TIMEOUT_S = 10
    start = time()
    while not (__fw_version_valid() or (time() - start) > TIMEOUT_S):
        ThermalMonitor.request_packet()
        if __fw_version_valid():
            conf["log"].debug(f"Packet Received: \n{ThermalMonitor.packet}")
            return None
    conf["log"].debug(f"Packet Received: \n{ThermalMonitor.packet}")
    return "Could not communicate over SPI"

def get_tc_temp(tc_ch):
    if tc_ch not in conf["tc"]["range"]:
        conf["log"].exception("Error, desired thermocouple number must be 1 or 2")
        raise ValueError
    else:
        ThermalMonitor.request_packet()
        conf["log"].debug(f"Packet Received: \n{ThermalMonitor.packet}")
        tc_temp = ThermalMonitor.packet.temp_sensor_C[tc_ch-1]
    return tc_temp

def __fan_speed_valid(fan_index):
    return ThermalMonitor.packet.fan_speed_rpm[fan_index] > 0

def get_fan_speed(fan_num):
    fan_speed = 0
    if fan_num not in conf["fan"]["range"]:
        conf["log"].exception("Error, desired fan number must be 1,2,3")
        raise ValueError
    else:
        ThermalMonitor.request_packet()
        conf["log"].debug(f"Packet Received: \n{ThermalMonitor.packet}")
        fan_speed = ThermalMonitor.packet.fan_speed_rpm[fan_num - 1]

    conf["log"].debug("Measured fan {:d}, speed: {:d} RPM".format(fan_num, fan_speed))

    return fan_speed
