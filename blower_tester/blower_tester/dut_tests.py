import logging
from collections import namedtuple
import subprocess as sp
import os

if os.name != 'nt': from smbus2 import SMBus
from .config import pins, thermocouple_tol, stm_bin_fd, fan_speed, fan_speed_tol

from .stm32 import do_spi_ack, get_tc_temp, set_fan_speed, get_fan_speed

def pwr_on():
    logging.debug("Asserting power enable pin")
    pins.pwr_en.value = True

def pwr_off():
    logging.debug("De-Asserting power enable pin")
    pins.pwr_en.value = False

def prog_mcu():
    logging.info("Programming MCU...")

    bin_dir = "{:s}/lib/{:s}".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), stm_bin_fd)

    #Not sure this is the correct address
    cmdline_args = ["st-flash", "--freq=4M", "--reset", "write", bin_dir, "0x8000000"]

    try:
        cmdline_process = sp.Popen(cmdline_args, stdout=sp.PIPE, stderr=sp.STDOUT)
        process_out, _ = cmdline_process.communicate()
        logging.debug(process_out.decode("utf-8"))

        if "flash written and verified" in process_out.decode("utf-8").lower():
            logging.info("Programming sucessful")
            err = None
        else:
            err = "Failed to program STM32!, check U4, check for shorts on 5V or 3.3V rail"

    except(OSError, sp.CalledProcessError) as exception:
        logging.error("Exception occured: {}".format(exception))
        err = "An error occurred, cannot program STM32!, check U4"

    return err

def spi_ack():
    logging.debug("Testing SPI communications to STM")

    err = do_spi_ack()

    if err is None: logging.debug("SPI communications check successful")
    else: logging.error("SPI communications check unsuccessful")

    return err

def _tmp1075_temp():
    ADDR = 0x48
    TEMP_REG = 0x00

    raw = SMBus(1).read_i2c_block_data(ADDR, TEMP_REG, 2)
    return ((raw[0] << 4) + (raw[1] >> 4)) * 0.0625

def test_tc1():
    tc1_temp = get_tc_temp(1)
    return _check_tc(1, tc1_temp, "U1, L1, L2, R4, R6, R7, C1, CN3")

def test_tc2():
    tc2_temp = get_tc_temp(2)
    return _check_tc(2, tc2_temp, "U2, L3, L4, R11, R13, R14, C3, CN4")

def _check_tc(tc_num, tc_temp, fail_designators):
    room_temp = _tmp1075_temp()

    logging.debug("Room Temperature: {:.2f} C".format(room_temp))
    logging.debug("Thermocouple {:d} Temperature: {:.2f} C".format(tc_num, tc_temp))

    if 100 * abs((tc_temp - room_temp) / room_temp) < thermocouple_tol:
        err = None
        logging.debug("Thermocouple {:d} test pass".format(tc_num))

    else:
        err = "Thermocouple {:d} test failure, check {:s}".format(tc_num, fail_designators)

    return err

def _check_fan(fan_num, desired_rpm, fail_designators):
    desired_rpm = int(desired_rpm)

    logging.debug("Attempting to spin fan {:d} at {:d} rpm".format(fan_num, desired_rpm))
    
    #Please call some function here to spin the fan
    set_fan_speed(fan_num, fan_speed)
    measured_rpm = int(get_fan_speed(fan_num)) #Change this to the actual measured RPM value

    logging.debug("Measured fan {:d} RPM: {:d}".format(fan_num, measured_rpm))

    if 100 * abs((desired_rpm - measured_rpm) / desired_rpm) < fan_speed_tol:
        err = None
        logging.debug("Fan {:d} test pass".format(fan_num))

    else:
        err = "Fan {:d} test failure, check {:s}".format(fan_num, fail_designators)

    return err

def test_fan1():
    return _check_fan(1, fan_speed, "R18, R19, R25, C12, D4, Q1")

def test_fan2():
    return _check_fan(2, fan_speed, "R20, R21, R26, C13, D5, Q2")

def test_fan3():
    return _check_fan(3, fan_speed, "R22, R23, R29, C14, D6, Q3")

def get_test_seq():
    dut_test = namedtuple("dut_test", ["name", "func", "prompt", "debug_prompt"])

    #Offer debug prompts for manual tests which fail
    return [
        dut_test("program MCU",    prog_mcu,   None,          None),
        dut_test("SPI comms",      spi_ack,    None,          None),
        dut_test("thermocouple 1", test_tc1,   None,          None),
        dut_test("thermocouple 2", test_tc2,   None,          None),
        dut_test("fan 1",          test_fan1,  None,          None),
        dut_test("fan 2",          test_fan2,  None,          None),
        dut_test("fan 3",          test_fan3,  None,          None)
    ]
