import warnings
warnings.simplefilter('ignore')

from subprocess import check_output
from gpiozero import OutputDevice, Button
import logging

class text_colour:
    bold = '\033[35m'
    green = '\033[32m'
    yellow = '\033[33m'
    red = '\033[31m'
    rst = '\033[0m'

conf = {
    "fan": {
        "range"        : range(1, 5),
        "duty"         : 50, #%
        "speed"        : 7500, #rpm of fans on test fixture
        "tol"          : 30, #%
        "settling_time": 10, #takes a few seconds to stablize
        "fail_desig"   : "U7, U8 and connected components"
    },

    "ftdi": {
        "vid"       : "0403", #string
        "pid"       : "6015", #string
        "conf_fd"   : "ft231x_conf",
        "fail_desig": "U9 and connected components"
    },

    "hdc": {
        "min_temp"  : 5,  #C
        "max_temp"  : 50, #C
        "fail_desig": "U10"
    },

    "log": logging.getLogger(__name__),

    "spi": {
        "fail_desig": "U14, U15 and connected components"
    },

    "stm": {
        "bin_fd"      : "test_fixture_thermal_monitor.bin",
        "bin_addr"    : "0x8000000",  #string type
        "option_bytes": "0xDEFFE1AA", #string type
        "flash_baud"  :  "921600",
        "fail_desig"  : "for shorts/opens on 5V or 3.3V rail, L1, U6"
    },

    "tc": {
        "range": range(1, 4),
        "min_temp"  : 5,  #C
        "max_temp"  : 50, #C
        "fail_desig": "U5, U17 and connected components"
    },

    "tmp1075": {
        "addr"             : 0x49,
        "temp_reg"         : 0x00,
        "pcb_plane_delta_c": 12
    }
}

def act_hw():
    act_hw = False

    try:
        if "Raspberry Pi 5 Model B" in check_output(["cat",
		"/sys/firmware/devicetree/base/model"]).decode("utf-8"):
            act_hw = True
            conf["log"].debug("Running on actual hardware")

    except: conf["log"].debug("Not running on actual hardware")

    return act_hw

class pins:
    if act_hw():
        ptt  = Button(5)
        ptt.hold_time = 10
        ptt_led_ctrl = OutputDevice(16, initial_value=False)
        dut_pwr_en   = OutputDevice(26, initial_value=False)

