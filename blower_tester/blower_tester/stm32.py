from .config import conf
from .thermal_monitor import ThermalMonitor

def __fw_version_valid():
    return ThermalMonitor.packet.fw_version_major > 0

def do_spi_ack():
    ThermalMonitor.request_packet()
    conf["log"].debug(f"Packet Received: \n{ThermalMonitor.packet}")
    return None if __fw_version_valid() else "Could not communicate over SPI"

def get_tc_temp(tc_ch):
    if tc_ch not in conf["tc"]["range"]:
        conf["log"].exception("Error, desired thermocouple number must be 1 or 2")
        raise ValueError
    else:
        ThermalMonitor.request_packet()
        conf["log"].debug(f"Packet Received: \n{ThermalMonitor.packet}")
        tc_temp = ThermalMonitor.packet.temp_sensor_C[tc_ch-1]
    return tc_temp

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
