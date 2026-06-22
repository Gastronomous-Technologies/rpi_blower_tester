import time
from sys import stdin
from select import select

from .config import text_colour as tc, act_hw, conf, pins
from .dut_tests import get_test_seq, dut_pwr_on, dut_pwr_off

def disp_start_info():
    conf["log"].info(f"{tc.bold}CG6-CHAS-E-019 Blower/Thermocouple Tester{tc.rst}\n"
                     "Supports CG6-CHAS-E-019 Version v1.5+ PCBAs\n"
                     "All prompts refer to the board under test\n")

def test_brd():
    test_index = 0
    exit_test = False

    dut_pwr_on()

    test_seq = get_test_seq()
    if test_seq is None:
        conf["log"].critical("No testing sequence loaded!")
        raise ValueError

    while test_index < len(test_seq):
        test_def = test_seq[test_index]

        err, check_parts_str = test_def.func()
        if err:
            conf["log"].debug(f"{test_def.name} failed, retrying...")
            err, check_parts_str = test_def.func() #try again if fails

        test_res = f"{tc.green}PASS" if err is False else f"{tc.red}FAIL"
        conf["log"].info(f"{test_def.name}: {test_res}{tc.rst}")

        if err is True:
            conf["log"].info(f"Check {check_parts_str}")
            exit_test = True

        if exit_test: test_index = len(test_seq)
        else: test_index += 1

    dut_pwr_off()

    brd_err = True if exit_test else False

    return brd_err

def blower_main():
    disp_start_info()
    brd_num = 0

    if act_hw():
        ptt_held = False
 
        while not ptt_held:
            conf["log"].info("Please place board into tester")
            complete_test = False

            if brd_num == 0:
                conf["log"].info("Press push to test button or enter key to test GOOD PCBA")
            else:
                conf["log"].info("Press push to test button or enter key to test board {:d}".format(brd_num))

            conf["log"].info(f"Hold push to test button for {pins.ptt.hold_time} seconds to shutdown")

            while not complete_test:
                enter_pressed, _, _ = select([stdin], [], [], 0)

                if enter_pressed: 
                    complete_test = True
                    stdin.readline().rstrip() #Clear the press

                if pins.ptt.is_pressed and not ptt_held:
                    while pins.ptt.is_pressed:
                        time.sleep(0.1)
                        if pins.ptt.is_held:
                            ptt_held = True
                            conf["log"].info("Release button to start computer shutdown")
                            time.sleep(3)
                    if ptt_held: break
                    else: complete_test = True

            if complete_test:
                pins.ptt_led_ctrl.value = True
                err = test_brd()
                pins.ptt_led_ctrl.value = False

                test_res = f"{tc.green}PASS" if not err else f"{tc.red}FAIL"
                conf["log"].info(f"\nBoard test complete, result is {test_res}{tc.rst}\n")

                time.sleep(2)
                conf["log"].info("Unload current PCBA")

                brd_num += 1

    else:
        conf["log"].exception("Cannot execute actual program"
                              "if not running on Raspberry Pi 5 Model B")
        raise Exception

    conf["log"].info("Exiting application...")