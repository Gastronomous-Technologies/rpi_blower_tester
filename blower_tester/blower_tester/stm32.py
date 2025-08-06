import time

from .config import conf
from .thermal_monitor import TMStatusPacket

def __fw_version_valid(packet):
    return packet.fw_version_major > 0

def do_spi_ack(thermal_monitor):
    TIMEOUT_S = 10
    packet = TMStatusPacket()
    start = time.time()
    while not (__fw_version_valid(packet) or (time.time() - start) > TIMEOUT_S):
        thermal_monitor.request_packet()
        packet = thermal_monitor.packet
        if __fw_version_valid(packet):
            conf["log"].debug(f"Packet Received: \n{thermal_monitor.packet}")
            return None
    conf["log"].debug(f"Packet Received: \n{thermal_monitor.packet}")
    return "Could not communicate over SPI"

def get_tc_temp(thermal_monitor, tc_ch):
    if tc_ch not in conf["tc"]["range"]:
        conf["log"].exception("Error, desired thermocouple number must be 1 or 2")
        raise ValueError
    else:
        for i in range(5):
            thermal_monitor.request_packet()
            conf["log"].debug(f"Packet Received: \n{thermal_monitor.packet}")
        tc_temp = thermal_monitor.packet.temp_sensor_C[tc_ch-1]
    return tc_temp

def __fan_speed_valid(packet, fan_index):
    return packet.fan_speed_rpm[fan_index] > 0

def get_fan_speed(thermal_monitor, fan_num):
    fan_speed = 0
    if fan_num not in conf["fan"]["range"]:
        conf["log"].exception("Error, desired fan number must be 1,2,3")
        raise ValueError
    else:
        TIMEOUT_S = 10
        packet = TMStatusPacket() 
        start = time.time()
        while not (__fan_speed_valid(packet, fan_num-1) or (time.time() - start) > TIMEOUT_S):
            thermal_monitor.request_packet()
            packet = thermal_monitor.packet
            if __fan_speed_valid(packet, fan_num-1):
                conf["log"].debug(f"Packet Received: \n{thermal_monitor.packet}")
                fan_speed = thermal_monitor.packet.fan_speed_rpm[fan_num-1]
                break

    conf["log"].debug("Measured fan {:d}, speed: {:d} RPM".format(fan_num, fan_speed))
    return fan_speed
