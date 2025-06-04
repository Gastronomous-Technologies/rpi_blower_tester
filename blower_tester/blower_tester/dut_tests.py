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

def _spin_fan2():
    pass

def _spin_fan3():
    pass

dut_test = namedtuple("dut_test", ["name", "func", "prompt", "debug_prompt"])

test_seq = [
    dut_test("power LEDs",     _pwr_on,    "Two leds on?", "for power shorts/opens"),
    dut_test("program MCU",    _prog_mcu,   None,          None),
    dut_test("thermocouple 1", _meas_tc1,   None,          None),
    dut_test("thermocouple 2", _meas_tc2,   None,          None),
    dut_test("fan 1",          _spin_fan1,  "Fan 1 spun?", "Q1 or R25"),
    dut_test("fan 2",          _spin_fan2,  "Fan 2 spun?", "Q2 or R26"),
    dut_test("fan 3",          _spin_fan3,  "Fan 3 spun?", "Q2 or R29")
]
