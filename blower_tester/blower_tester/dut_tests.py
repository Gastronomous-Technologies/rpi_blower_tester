from collections import namedtuple
import time
import subprocess as sp
from pathlib import Path
import pyudev
from pyftdi.ftdi import Ftdi
from pyftdi.eeprom import FtdiEeprom
from pyftdi.usbtools import UsbTools

from .thermal_monitor import ThermalMonitor
from .config import pins, conf, act_hw
if act_hw(): from smbus2 import SMBus
from .config import text_colour as colour

from .stm32 import get_firmware_version, get_tc_temp, get_fan_speed, get_hdc_temp

__thermal_monitor = ThermalMonitor(0, 0, 50000, 0)

def dut_pwr_on():
    conf["log"].debug("Asserting power enable pin")
    pins.dut_pwr_en.value = True
    time.sleep(3)
    __thermal_monitor.start()

def dut_pwr_off():
    conf["log"].debug("De-Asserting power enable pin")
    __thermal_monitor.stop()
    pins.dut_pwr_en.value = False
    time.sleep(0.5)

def set_mcu_option_bytes():
    err = True
    conf["log"].debug("Setting MCU option bytes...")

    try:
        sp.check_call(["st-flash", "--area=option",
                       "write", conf["stm"]["option_bytes"]],
                        stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        dut_pwr_off()
        dut_pwr_on() #power cycle required for settings to take affect
        err = False

    except sp.CalledProcessError as e:
        conf["log"].debug(f"Setting option bytes exit code {e.returncode}")

    return err, conf["stm"]["fail_desig"]

def __get_ftdi_device_node():
    context = pyudev.Context()
    ftdi_device_node = None

    for device in context.list_devices(subsystem='tty'):
        if device.get('ID_VENDOR_ID') == conf["ftdi"]["vid"] and \
           device.get('ID_MODEL_ID')  == conf["ftdi"]["pid"]:
            ftdi_device_node = device.device_node
            conf["log"].debug(f"ftdi_device_node: {ftdi_device_node}")

    return ftdi_device_node

def configure_ftdi():
    err = True
    ftdi_device_found = False

    conf["log"].debug("Configuring FTDI...")
    UsbTools.flush_cache()

    try:
        ftdi_devices = Ftdi.list_devices(url="ft-x")
        if ftdi_devices: ftdi_device_found = True
    except:
        conf["log"].error("No FTDI devices found!")

    if ftdi_device_found:
        if len(ftdi_devices) > 1:
            conf["log"].exception("More than one FTDI device found!, please service test fixture")
            raise Exception
        else:
            ftdi_conf_file = "{}/lib/{:s}".format(Path(__file__).resolve().parent, conf["ftdi"]["conf_fd"])
            conf["log"].debug(f"FTDI config file: {ftdi_conf_file}")
            ftdi_device_url = f"ftdi://ftdi:ft-x:{ftdi_devices[0][0].sn}/1" #grab the serial number

            try:
                sp.check_call(["ftconf.py", ftdi_device_url, "-i", ftdi_conf_file, "-l", "values", "-u"])

                conf["log"].debug("FTDI configuration written to device")

                dut_pwr_off()
                dut_pwr_on() #power cycle required for settings to take affect

                err = False
                conf["log"].debug("Configuration written, reloading ftdi_sio")

                sp.check_call(["sudo", "modprobe", "-r", "ftdi_sio"])
                sp.check_call(["sudo", "modprobe", "ftdi_sio"])

            except sp.CalledProcessError as e:
                conf["log"].debug(f"Configuring FTDI exit code {e.returncode}")

    return err, conf["ftdi"]["fail_desig"]

def program_microcontroller():
    err = True

    conf["log"].debug("Programming MCU...")

    stm32_bin = "{}/lib/{:s}".format(Path(__file__).resolve().parent, conf["stm"]["bin_fd"])
    conf["log"].debug(f"stm32 binary: {stm32_bin}")

    ftdi_device_node = __get_ftdi_device_node()

    if ftdi_device_node is not None:
        try:
            cmdline_args = ["stm32flash", "-w", stm32_bin, "-v", "-g", "0x0", "-i",
                                "rts&dtr,-dtr,:-rts&dtr,-dtr,,",
                                "-b", conf["stm"]["flash_baud"], ftdi_device_node]
            sp.check_call(cmdline_args, stdout=sp.PIPE, stderr=sp.STDOUT)
            err = False

        except sp.CalledProcessError as e:
            conf["log"].debug(f"MCU programming exit code {e.returncode}")

    else:
        conf["log"].debug("Cannot find ftdi device node")

    return err, conf["stm"]["fail_desig"]

def check_fw_version():
    conf["log"].debug("Testing SPI communications to STM")
    time.sleep(3) #Allow the MCU to boot and start sending information

    err = get_firmware_version(__thermal_monitor)

    if err is False:
        conf["log"].debug("SPI communications check successful")
    else:
        conf["log"].error("SPI communications check unsuccessful")

    return err, conf["spi"]["fail_desig"]

def check_onboard_temp():
    err = True
    conf["log"].debug("Testing HDC2010 onboard temperature sensor")
    hdc_temp = get_hdc_temp(__thermal_monitor)

    if hdc_temp > conf["hdc"]["min_temp"] and hdc_temp < conf["hdc"]["max_temp"]:
        conf["log"].debug("HDC2010 onboard temperature sensor test pass")
        err = False
    else:
        conf["log"].debug("HDC2010 onboard temperature sensor failure")

    return err, conf["hdc"]["fail_desig"]

def _tmp1075_temp():
    tmp1075_addr = conf["tmp1075"]["addr"];
    temp_reg = conf["tmp1075"]["temp_reg"]

    raw = SMBus(1).read_i2c_block_data(tmp1075_addr, temp_reg, 2)
    return ((raw[0] << 4) | (raw[1] >> 4)) * 0.0625 - conf["tmp1075"]["pcb_plane_delta_c"]

def check_thermocouples():
    err = True
    err_str = ""
    tc_errors = []

    conf["log"].debug("Testing thermocouples")

    for tc_num in conf["tc"]["range"]:
        tc_err  = _check_thermocouple(tc_num)
        if tc_err: err_str += f"{conf["tc"]["fail_desig"]} on thermocouple channel {tc_num}\n"
        tc_errors.append(tc_err)

    if all(tc_err == False for tc_err in tc_errors) :
        err = False
        conf["log"].debug("All thermocouples operate as intended")

    return err, err_str

def _check_thermocouple(tc_num):
    err = True

    tc_temp = get_tc_temp(__thermal_monitor, tc_num)
    conf["log"].debug(f"Thermocouple {tc_num} Temperature: {tc_temp :.2f} C")
    if tc_temp > conf["tc"]["min_temp"] and tc_temp < conf["tc"]["max_temp"]:
        conf["log"].debug(f"Thermocouple {tc_num} test pass")
        err = False
    else:
        conf["log"].error(f"Thermocouple {tc_num} failure")

    return err

def check_fans():
    err = True
    err_str = ""
    fan_errors = []

    conf["log"].debug("Allowing fan speeds to stablize")
    time.sleep(conf["fan"]["settling_time"])

    desired_rpm = conf["fan"]["speed"] * conf["fan"]["duty"] / 100.0
    for fan in conf["fan"]["range"]:
        fan_err = _check_fan(fan, desired_rpm)
        if fan_err: err_str += f"{conf["fan"]["fail_desig"]} on fan channel {fan}\n"
        fan_errors.append(fan_err)

    if all(fan_err == False for fan_err in fan_errors) :
        err = False
        conf["log"].debug("All fans operate as intended")

    return err, err_str

def _check_fan(fan_num, desired_rpm):
    err = True

    conf["log"].debug(f"Attempting to spin fan {fan_num} at {desired_rpm} RPM")

    measured_rpm = int(get_fan_speed(__thermal_monitor, fan_num))

    conf["log"].debug(f"Measured fan {fan_num} RPM: {measured_rpm}")

    if desired_rpm != 0:
        percent_error = 100 * abs((desired_rpm - measured_rpm) / desired_rpm)
        conf["log"].debug(f'Fan % error: {percent_error}')

        if percent_error < conf["fan"]["tol"]:
            err = False
        else:
            conf["log"].error(f"Fan {fan_num} test failure")

    elif desired_rpm == 0 and measured_rpm == 0:
        err = False

    else:
        conf["log"].exception(f"Invalid fan speed: {measured_rpm} for fan {fan_num}")
        raise ValueError

    test_res = "pass" if err == False else True
    conf["log"].debug(f"Fan {fan_num} test {test_res}")

    return err

def erase_mcu_flash():
    err = True
    conf["log"].debug("Erasing MCU...")

    dut_pwr_off()
    dut_pwr_on()

    try:
        sp.check_call(["st-flash", "reset"],
                        stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        err = False

    except sp.CalledProcessError as e:
        conf["log"].debug(f"Erasing MCU failure code {e.returncode}")

    return err, conf["stm"]["fail_desig"]

def get_test_seq():
    dut_test = namedtuple("dut_test", ["name", "func"])

    return [
        dut_test("Setting option bytes", set_mcu_option_bytes   ),
        dut_test("Configuring FTDI",     configure_ftdi         ),
        dut_test("Programming MCU",      program_microcontroller),
        dut_test("SPI comms",            check_fw_version       ),
        dut_test("Onboard temp",         check_onboard_temp     ),
        dut_test("Thermocouples",        check_thermocouples    ),
        dut_test("Fans",                 check_fans             ),
        dut_test("Erasing MCU",          erase_mcu_flash        )
    ]
