from .config import conf
from .thermal_monitor import ThermalMonitor
from time import time

def __check_cond_within_timeout(condition, timeout=10):
    start = time()
    while not condition() or time() - start > timeout:
        ThermalMonitor.request_packet()
        if condition():
            return True
    return False

def __fw_version_valid():
    return ThermalMonitor.packet.fw_version_major > 0

def do_spi_ack():
    result = __check_cond_within_timeout(lambda: __fw_version_valid())
    err = None if result else "Could not communicate over SPI"
    return err

def __fw_version_valid():
    return ThermalMonitor.fw_version_major > 0

def do_spi_ack():
    TIMEOUT_S = 10
    start = time()
    while not (__fw_version_valid() or (time() - start) > TIMEOUT_S):
        ThermalMonitor.request_packet()
        if __fw_version_valid():
            conf["log"].debug(f"Packet Received: \n{ThermalMonitor.packet}")
            return None
    conf["log"].debug(f"Packet Received: \n{Thermal_Monitor.packet}")
    return "Could not communicate over SPI"


def get_tc_temp(tc_ch):
    if tc_ch not in conf["tc"]["range"]:
        conf["log"].exception("Error, desired thermocouple number must be 1 or 2")
        raise ValueError
    else:
        ThermalMonitor.request_packet()
        tc_temp = ThermalMonitor.packet.temp_sensor_C[tc_ch-1]
    return tc_temp

def get_fan_speed(fan_num):
    if fan_num not in conf["fan"]["range"]:
        conf["log"].exception("Error, desired fan number must be 1,2,3")
        raise ValueError

    else:
        ThermalMonitor.request_packet()
        fan_speed = ThermalMonitor.packet.fan_speed_rpm[fan_num-1]
        conf["log"].debug("Measured fan {:d}, speed: {:d} RPM".format(fan_num, fan_speed))

        for i in range(5):
            thermal_monitor.request_packet()
            conf["log"].debug(f"Packet Received: \n{thermal_monitor.packet}")

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
        start = time()
        while not (__fan_speed_valid(packet, fan_num-1) or (time() - start) > TIMEOUT_S):
            thermal_monitor.request_packet()
            packet = thermal_monitor.packet
            if __fan_speed_valid(packet, fan_num-1):
                conf["log"].debug(f"Packet Received: \n{thermal_monitor.packet}")
                fan_speed = thermal_monitor.packet.fan_speed_rpm[fan_num-1]
                break
    conf["log"].debug("Measured fan {:d}, speed: {:d} RPM".format(fan_num, fan_speed))
>>>>>>> sm/ES-1441/thermal-monitor-test-impl
    return fan_speed
