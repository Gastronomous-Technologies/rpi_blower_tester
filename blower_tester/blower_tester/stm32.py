from .config import conf

def do_spi_ack():
    err = None
    return err

def get_tc_temp(tc_ch):
    if tc_ch not in conf["tc"]["range"]:
        conf["log"].exception("Error, desired thermocouple number must be 1 or 2")
        raise ValueError

    else:
        tc_temp = 25 #Need to update this

    return tc_temp

def set_fan_speed(fan_num, fan_speed):
    if fan_num not in conf["fan"]["range"]:
        conf["log"].exception("Error, desired fan number must be 1,2,3")
        raise ValueError

    else:
        pass #Set the fan speed

def get_fan_speed(fan_num):
    if fan_num not in conf["fan"]["range"]:
        conf["log"].exception("Error, desired fan number must be 1,2,3")
        raise ValueError

    else:
        fan_speed = 5000 #Please change this
        conf["log"].debug("Measured fan {:d}, speed: {:d} RPM".format(fan_num, fan_speed))

    return fan_speed
