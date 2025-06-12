import warnings
warnings.simplefilter('ignore')

from gpiozero import OutputDevice, InputDevice

class text_colour:
    bold = '\033[35m'
    green = '\033[32m'
    yellow = '\033[33m'
    red = '\033[31m'
    rst = '\033[0m'

class pins:
    alert  = InputDevice(4)
    pwr_en = OutputDevice(26, initial_value=False)

thermocouple_tol = 30 #%

stm_bin_fd = "thermal_monitor.bin"

fan_speed_tol = 10 #%
fan_speed = 5000 #RPM

tmp1075_addr = 0x48
