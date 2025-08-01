from .config import conf, act_hw
if act_hw(): import spidev
import struct

class TMStatusPacket:
    PACKET_SOF = 170
    PACKET_SIZE = 30
    def __init__(self):
        self.fw_version_major = 0
        self.fw_version_minor = 0
        self.fw_version_patch = 0
        self.temp_sensor_C = [0.,0.]
        self.temp_board_C = [0.,0.]
        self.fan_speed_rpm = [0, 0, 0]
        self.error_flags = 0

    def load_from_buff(self, buff):
        unpacked_data = struct.unpack('<BBBffffHHHI', bytes(buff))
        self.fw_version_major = unpacked_data[0]
        self.fw_version_minor = unpacked_data[1]
        self.fw_version_patch = unpacked_data[2]
        self.temp_sensor_C = unpacked_data[3:5]
        self.temp_board_C = unpacked_data[5:7]
        self.fan_speed_rpm = unpacked_data[7:10]
        self.error_flags = unpacked_data[10]

    def __str__(self):
        return f"""
        FW Ver: {self.fw_version_major}.{self.fw_version_minor}.{self.fw_version_patch}
        Temp Sensor C: {self.temp_sensor_C[0]}C, {self.temp_sensor_C[1]}C
        Temp Board C: {self.temp_board_C[0]}C, {self.temp_board_C[1]}C
        Fan Speed: {self.fan_speed_rpm[0]}RPM, {self.fan_speed_rpm[1]}RPM, {self.fan_speed_rpm[2]}RPM
        Error Flags: {self.error_flags}
        """

class ThermalMonitor:
    def __init__():
        ThermalMonitor.bus_id = conf["bus_id"]
        ThermalMonitor.device_id = conf["device_id"]
        ThermalMonitor.clock_speed = conf["clock_speed"]
        ThermalMonitor.spi_mode = conf["spi_mode"]
        ThermalMonitor.spi_inst = spidev.SpiDev()
        ThermalMonitor.packet = TMStatusPacket()

    def start():
        ThermalMonitor.packet = TMStatusPacket()
        ThermalMonitor.spi_inst.open(ThermalMonitor.bus_id, ThermalMonitor.device_id)
        ThermalMonitor.spi_inst.max_speed_hz = ThermalMonitor.clock_speed
        ThermalMonitor.spi_inst.mode = ThermalMonitor.spi_mode

    def request_packet():
        fail_count = 0
        packet_started = False
        while not packet_started and fail_count < TMStatusPacket.PACKET_SIZE:
            recv = ThermalMonitor.spi_inst.xfer([0], ThermalMonitor.clock_speed, 1, 8)
            packet_started = recv[0] == TMStatusPacket.PACKET_SOF
            if not packet_started:
                fail_count = fail_count + 1
        if fail_count >= TMStatusPacket.PACKET_SIZE:
            fail_count = 0
        else:
            payload = [0] * (TMStatusPacket.PACKET_SIZE-1)
            recv = ThermalMonitor.spi_inst.xfer(payload, ThermalMonitor.clock_speed, 1, 8)

        ThermalMonitor.packet.load_from_buff(recv)

    def stop():
        ThermalMonitor.spi_inst.close()