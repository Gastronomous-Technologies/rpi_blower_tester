import warnings
warnings.simplefilter('ignore')

from subprocess import check_output
from gpiozero import OutputDevice, InputDevice
import logging

class text_colour:
    bold = '\033[35m'
    green = '\033[32m'
    yellow = '\033[33m'
    red = '\033[31m'
    rst = '\033[0m'

conf = {

    "tc": {
        "range": range(1,3),
        "tol"  : 30 #%
    },

    "tmp1075_addr": 0x48,

    "fan": {
        "range": range(1,4),
        "speed": 7800, #rpm
        "tol"  :  20 #%
    },

    "stm": {
        "bin_fd" : "thermal_monitor.bin",
        "addr"   : "0x8000000" #string type
    },

    "tm": {
        "bus_id":      0,
        "device_id":   0, 
        "clock_speed": 50000, 
        "spi_mode":    0
    },

    "log": logging.getLogger(__name__)
}

def act_hw():
    act_hw = False

    try:
        if "Raspberry Pi Zero 2 W" in check_output(["cat",
		"/sys/firmware/devicetree/base/model"]).decode("utf-8"):
            act_hw = True
            conf["log"].debug("Running on actual hardware")

    except: conf["log"].debug("Not running on actual hardware")

    return act_hw

class pins:
    if act_hw():
        alert  = InputDevice(4)
        pwr_en = OutputDevice(26, initial_value=False)
