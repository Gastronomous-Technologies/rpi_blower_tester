from gpiozero import OutputDevice, InputDevice

class text_colour:
    bold = '\033[35m'
    green = '\033[32m'
    yellow = '\033[33m'
    red = '\033[31m'
    rst = '\033[0m'

class pins:
    alert  = InputDevice(4)
    cs     = OutputDevice(8, initial_value=True)
    pwr_en = OutputDevice(26, initial_value=False)

thermocouple_tol = 10 #%
