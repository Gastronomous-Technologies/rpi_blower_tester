import time

from .config import text_colour as tc, act_hw, conf
from .dut_tests import get_test_seq, pwr_on, pwr_off

def disp_start_info():
    conf["log"].info(f"{tc.bold}CG5-ELEC-E-019 BlowerThermocouple Tester{tc.rst}")
    conf["log"].info("Supports Version v2.1+ PCBs\n")

    display_guide = False
    for test in get_test_seq():
        if test.prompt is not None: display_guide = True

    if display_guide:
        conf["log"].info("Enter y (yes) to confirm and complete next test")
        conf["log"].info("Enter n (no) to offer debug and retest")
        conf["log"].info("Enter ? (unsure) to retest")
        conf["log"].info("Enter e (exit) to exit test")

    conf["log"].info("All prompts refer to the board under test\n")

def handle_user_prompt(test_def):
    early_exit = False
    res = input()

    while res not in {'y', 'e'}:

        if res == 'n':
            conf["log"].error("Check {:s}".format(test_def.debug_prompt))
            time.sleep(2)

        if res == 'n' or res == '?':
            conf["log"].info("Testing {:s}: {:s}".format(test_def.name, test_def.prompt.lower()))
            test_def.func()

        else:
            conf["log"].error("Unrecognized command, please try again...")

        res = input()

    if res == 'e':
        conf["log"].info("Exiting test sequence")
        early_exit = True

    return early_exit

def test_brd():
    test_index = 0
    exit_test = False

    pwr_on()
    test_seq = get_test_seq()
    if test_seq is None:
        conf["log"].critical("No testing sequence loaded!")
        raise ValueError

    while test_index < len(test_seq):
        test_def = test_seq[test_index]

        #Test requires user input
        if test_def.prompt is not None:
            conf["log"].info("Testing {:s}".format(test_def.name))
            err_msg = test_def.func()
            conf["log"].info(test_def.prompt)

            if err_msg is None: exit_test = handle_user_prompt(test_def)

        #Automatic test
        else:
            err_msg = test_def.func()
            test_res = "Passed" if err_msg is None else "Failed"
            conf["log"].info("Testing {:s}: {:s}".format(test_def.name, test_res))

        if err_msg is not None:
            exit_test = True
            conf["log"].error(err_msg)

        if exit_test: test_index = len(test_seq)
        else: test_index += 1

    pwr_off()
    brd_err = True if exit_test else False

    return brd_err

def blower_main():

    disp_start_info()
    brd_num = 0

    if act_hw():
        while True:
            conf["log"].info("Please connect ethernet cable to test board and socket board into tester")

            if brd_num == 0:
                conf["log"].info("Press enter to test GOOD PCBA")

            else:
                conf["log"].info("Press enter to test board {:d}".format(brd_num))

            input() #Delay starting test sequence until user is ready
            err = test_brd()

            test_res = f"{tc.green}PASS" if not err else f"{tc.red}FAIL"
            conf["log"].info(f"Board test complete, result is {test_res}{tc.rst}\n")

            time.sleep(2)
            conf["log"].info("Unload current PCBA and hit enter")
            input()

            brd_num += 1

    else:
        conf["log"].exception("Cannot execute actual program if not Running on RPI Zero 2 W")
        raise Exception
