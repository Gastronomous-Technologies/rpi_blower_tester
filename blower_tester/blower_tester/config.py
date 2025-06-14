import logging
import warnings
from subprocess import check_output

warnings.simplefilter('ignore')

from gpiozero import OutputDevice, InputDevice

class text_colour:
    bold = '\033[35m'
    green = '\033[32m'
    yellow = '\033[33m'
    red = '\033[31m'
    rst = '\033[0m'

def running_on_act_hw():
    act_hw = False

    try:
        if check_output(["cat", "/sys/firmware/devicetree/base/model", 
                                "||", "grep", "Raspberry Pi Zero 2 W"]):
            act_hw = True
            logging.debug("Running on actual hardware")

    except: logging.debug("Not running on actual hardware")

    return act_hw

class pins:
    if running_on_act_hw():
        alert  = InputDevice(4)
        pwr_en = OutputDevice(26, initial_value=False)

thermocouple_tol = 30 #%
thermocouple_range = range(1,3)

stm_bin_fd = "thermal_monitor.bin"

fan_speed_tol = 10 #%
fan_speed = 5000 #RPM
fan_range = range(1,4)

tmp1075_addr = 0x48
