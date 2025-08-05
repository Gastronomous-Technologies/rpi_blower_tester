from .config import act_hw
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
    def __init__(self, bus_id, device_id, clock_speed, spi_mode):
        self.bus_id = bus_id
        self.device_id = device_id
        self.clock_speed = clock_speed
        self.spi_mode = spi_mode
        self.spi_inst = spidev.SpiDev()
        self.packet = TMStatusPacket()

    def start(self):
        self.spi_inst.open(self.bus_id, self.device_id)
        self.spi_inst.max_speed_hz = self.clock_speed
        self.spi_inst.mode = self.spi_mode

    def request_packet(self):
        fail_count = 0
        packet_started = False
        while not packet_started and fail_count < TMStatusPacket.PACKET_SIZE:
            recv = self.spi_inst.xfer([0], self.clock_speed, 1, 8)
            packet_started = recv[0] == TMStatusPacket.PACKET_SOF
            if not packet_started:
                fail_count = fail_count + 1
        if fail_count >= TMStatusPacket.PACKET_SIZE:
            fail_count = 0
        else:
            payload = [0] * (TMStatusPacket.PACKET_SIZE-1)
            recv = self.spi_inst.xfer(payload, self.clock_speed, 1, 8)

        self.packet.load_from_buff(recv)

    def stop(self):
        self.spi_inst.close()

class MockThermalMonitor(ThermalMonitor):
    def __init__(self, bus_id, device_id, clock_speed, spi_mode):
        self.bus_id = bus_id
        self.device_id = device_id
        self.clock_speed = clock_speed
        self.spi_mode = spi_mode
        self.spi_inst = None
        self.packet = TMStatusPacket()