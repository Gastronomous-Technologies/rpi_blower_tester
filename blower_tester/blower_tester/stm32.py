from .config import conf
from .thermal_monitor import ThermalMonitor, TMStatusPacket
from time import time

def __check_cond_within_timeout(thermal_monitor, condition, timeout=10):
    packet = TMStatusPacket()
    start = time()
    while not condition() or time() - start > timeout:
        thermal_monitor.request_packet()
        packet = thermal_monitor.packet
        if condition():
            return True
    return False

def __fw_version_valid(packet):
    return packet.fw_version_major > 0

def do_spi_ack(thermal_monitor):
    result = __check_cond_within_timeout(thermal_monitor, lambda: __fw_version_valid(thermal_monitor.packet))
    err = None if result else "Could not communicate over SPI"
    return err


def get_tc_temp(thermal_monitor, tc_ch):
    if tc_ch not in conf["tc"]["range"]:
        conf["log"].exception("Error, desired thermocouple number must be 1 or 2")
        raise ValueError
    else:
        thermal_monitor.request_packet()
        tc_temp = thermal_monitor.packet.temp_sensor_C[tc_ch-1]
    return tc_temp

def get_fan_speed(thermal_monitor, fan_num):
    if fan_num not in conf["fan"]["range"]:
        conf["log"].exception("Error, desired fan number must be 1,2,3")
        raise ValueError

    else:
        thermal_monitor.request_packet()
        fan_speed = thermal_monitor.packet.fan_speed_rpm[fan_num-1]
        conf["log"].debug("Measured fan {:d}, speed: {:d} RPM".format(fan_num, fan_speed))

    return fan_speed
