import logging
from collections import namedtuple

from TMP1075 import TMP075
from .config import pins, thermocouple_tol

temp_sensor = TMP1075()

def pwr_on():
    logging.debug("Asserting power enable pin")
    pins.pwr_en.value = True

def pwr_off():
    logging.debug("De-Asserting power enable pin")
    pins.pwr_en.value = False

def prog_mcu():
    pass

def meas_tc1():
    tc1_temp = 25 #NOTE Get the temperature from the STM board instead
    return _check_tc(1, tc1_temp, "U1, L1, L2, R4, R6, R7, C1, CN3")

def meas_tc2():
    tc2_temp = 25 #NOTE Get the temperature from the STM board instead
    return _check_tc(2, tc2_temp, "U2, L3, L4, R11, R13, R14, C3, CN4")

def _check_tc(tc_num, tc_temp, designators):
    room_temp = temp_sensor.get_temperature()

    logging.debug("Room Temperature: {.2f} C".format(room_temp))
    logging.debug("Thermocouple {:d} Temperature: {.2f} C".format(tc_num, tc1_temp))

    if 100 * abs((tc1_temp - room_temp) / room_temp) < thermocouple_tol:
        err = None
        logging.debug("Thermocouple {:d} test pass")

    else:
        err = "Thermocouple {:d} test failure, check {:s}".format(tc_num, designators)

    return err

def meas_tc2():
    pass

def spin_fan1():
    pass

def spin_fan2():
    pass

def spin_fan3():
    pass

dut_test = namedtuple("dut_test", ["name", "func", "prompt", "debug_prompt"])

test_seq = [
    dut_test("power LEDs",     pwr_on,    "Two leds on?", "for power shorts/opens"),
    dut_test("program MCU",    prog_mcu,   None,          None),
    dut_test("thermocouple 1", meas_tc1,   None,          None),
    dut_test("thermocouple 2", meas_tc2,   None,          None),
    dut_test("fan 1",          spin_fan1,  None,          None),
    dut_test("fan 2",          spin_fan2,  None,          None),
    dut_test("fan 3",          spin_fan3,  None,          None)
]
