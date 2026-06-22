from .config import act_hw, conf
if act_hw(): import spidev
import struct


def _cobs_decode(data):
    """Decode COBS-encoded data. Input must include the trailing 0x00 delimiter."""
    data = bytes(data)
    out = bytearray()
    i = 0
    end = len(data)

    while i < end:
        code = data[i]
        if code == 0:
            break  # trailing 0x00 or garbage

        actual_code = min(code, end - i)
        i += 1

        out.extend(data[i:i + actual_code - 1])
        i += actual_code - 1

        if i >= end or data[i] == 0:
            break

        if code < 0xFF:
            out.append(0x00)

    return bytes(out)


class TMStatusPacket:
    COBS_PACKET_SIZE = 36
    CRC_SIZE = 2
    STRUCT_FMT = '<BBBffffHHHHI'  # 34 bytes: 3 ver + 3 tc temps + board temp + 4 fans + errors

    def __init__(self):
        self.fw_version_major = 0
        self.fw_version_minor = 0
        self.fw_version_patch = 0
        self.temp_sensor_C = [0., 0., 0.]
        self.temp_board_C = 0.
        self.fan_speed_rpm = [0, 0, 0, 0]
        self.error_flags = 0

    def _reset(self):
        self.fw_version_major = 0
        self.fw_version_minor = 0
        self.fw_version_patch = 0
        self.temp_sensor_C = [0., 0., 0.]
        self.temp_board_C = 0.
        self.fan_speed_rpm = [0, 0, 0, 0]
        self.error_flags = 0

    def load_from_buff(self, buff):
        try:
            decoded = _cobs_decode(buff)
            payload = decoded[:-self.CRC_SIZE]  # strip CRC16
            unpacked = struct.unpack_from(self.STRUCT_FMT, payload)
            self.fw_version_major = unpacked[0]
            self.fw_version_minor = unpacked[1]
            self.fw_version_patch = unpacked[2]
            self.temp_sensor_C = list(unpacked[3:6])
            self.temp_board_C = unpacked[6]
            self.fan_speed_rpm = list(unpacked[7:11])
            self.error_flags = unpacked[11]
        except Exception as e:
            self._reset()
            conf['log'].debug(f'Error deserializing packet: {e}')

    def __str__(self):
        return (
            f"\n        FW Ver: {self.fw_version_major}.{self.fw_version_minor}.{self.fw_version_patch}"
            f"\n        Temp Sensor C: {self.temp_sensor_C[0]}C, {self.temp_sensor_C[1]}C, {self.temp_sensor_C[2]}C"
            f"\n        Temp Board C: {self.temp_board_C}C"
            f"\n        Fan Speed: {self.fan_speed_rpm[0]}RPM, {self.fan_speed_rpm[1]}RPM, "
            f"{self.fan_speed_rpm[2]}RPM, {self.fan_speed_rpm[3]}RPM"
            f"\n        Error Flags: {self.error_flags}"
        )


class ThermalMonitor:
    def __init__(self, bus_id, device_id, clock_speed, spi_mode):
        self.bus_id = bus_id
        self.device_id = device_id
        self.clock_speed = clock_speed
        self.spi_mode = spi_mode
        self.spi_inst = spidev.SpiDev() if act_hw() else None
        self.packet = TMStatusPacket()

    def start(self):
        self.spi_inst.open(self.bus_id, self.device_id)
        self.spi_inst.max_speed_hz = self.clock_speed
        self.spi_inst.mode = self.spi_mode

    def request_packet(self):
        # Transfer full COBS packet in one transaction to keep CS asserted
        dummy = [0] * TMStatusPacket.COBS_PACKET_SIZE
        recv = self.spi_inst.xfer(dummy, self.clock_speed, 1, 8)
        conf['log'].debug(f'SPI recv: {[hex(b) for b in recv]}')
        self.packet.load_from_buff(recv)

    def stop(self):
        self.spi_inst.close()

    def has_valid_packet(self):
        return self.packet.fw_version_major + self.packet.fw_version_minor + self.packet.fw_version_patch
