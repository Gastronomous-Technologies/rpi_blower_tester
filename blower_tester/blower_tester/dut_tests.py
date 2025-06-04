import logging
from collections import namedtuple

from .config import pins

def _pwr_on():
    logging.debug("Asserting power enable pin")
    pins.pwr_en.value = True

def _prog_mcu():
    pass

def _meas_tc1():
    pass

def _meas_tc2():
    pass

def _spin_fan1():
    pass

dut_test = namedtuple("dut_test", ["name", "func", "prompt", "debug_prompt"])

test_seq = [
    dut_test("power LEDs",     _pwr_on,    "Two leds on?", "for power shorts/opens"),
    dut_test("program MCU",    _prog_mcu,   None,          "U4, cannot communicate"),
    dut_test("thermocouple 1", _meas_tc1,   None,          "CN3, U1 and passive components"),
    dut_test("thermocouple 2", _meas_tc2,   None,          "CN4, U2 and passive components"),
    dut_test("fan 1",          _spin_fan1,  None,          "tbd")
]
