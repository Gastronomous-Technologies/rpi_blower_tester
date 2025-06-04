from digitalio import DigitalInOut

class text_colour:
    bold = '\033[35m'
    green = '\033[32m'
    yellow = '\033[33m'
    red = '\033[31m'
    rst = '\033[0m'

class pins:
    import board
    alert  = DigitalInOut(board.D4)
    cs     = DigitalInOut(board.D8)
    pwr_en = DigitalInOut(board.D26)

def platform_check():
    platform = False
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'Raspberry Pi Zero 2 W' in m.read():
                platform = True

    except Exception:
        logging.warning("Hardware peripherals not available")
        logging.warning("Program can only be ran in test mode")

    return platform
