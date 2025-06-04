import logging
import time
import os
from subprocess import run
from digitalio import Direction

from .config import platform_check, pins
from .config import text_colour as tc

from .dut_tests import test_seq

def disp_start_info():
    logging.info(f"{tc.bold}CG5-ELEC-E-019 BlowerThermocouple Tester{tc.rst}")
    logging.info("Supports Version v2.1+ PCBs\n")
    logging.info("Enter y (yes) to confirm and complete next test")
    logging.info("Enter n (no) to offer debug and retest")
    logging.info("Enter ? (unsure) to retest")
    logging.info("Enter e (exit) to exit test")
    logging.info("All prompts refer to the board under test\n")

def initialize():
    logging.debug("Initializing GPIO pins")

    pins.alert.direction = Direction.INPUT
    pins.cs.direction = Direction.OUTPUT
    pins.pwr_en.direction = Direction.OUTPUT

    pins.cs.value = True
    pins.pwr_en.value = True

def handle_user_prompt(test_def):
    early_exit = False
    res = input()

    while res not in {'y', 'e'}:

        if res == 'n':
            logging.error("Check {:s}".format(test_def.debug_prompt))
            time.sleep(2)

        if res == 'n' or res == '?':
            logging.info("Testing {:s}: {:s}".format(test_def.name, test_def.prompt))
            test_def.func()

        else:
            logging.error("Unrecognized command, please try again...")

        res = input()

    if res == 'e':
        logging.info("Exiting test sequence")
        early_exit = True

    return early_exit

def blower_main():
    logging.basicConfig(format="%(levelname)s:      %(message)s",
                        datefmt='%s', level=logging.INFO)

    run("cls" if os.name == 'nt' else "clear", shell=True)

    if not platform_check():
        logging.critical("Blower main must be ran on Blower Thermocouple Tester: CG5-TEST-E-019")
        logging.critical("Exiting...")

        time.sleep(5)
        raise Exception

    disp_start_info()
    initialize()

    brd_num = 0

    while True:
        if brd_num == 0:
            logging.info("Press enter to test GOOD PCBA")
            input() #Delay starting test sequence until user is ready
        else:
            logging.info("PCBA {:d} test".format(brd_num))

        test_index = 0; exit_test = False

        while test_index < len(test_seq):
            test_def = test_seq[test_index]

            #Test requires user input
            if test_def.prompt is not None:
                logging.info("Testing {:s}".format(test_def.name))
                err_msg = test_def.func()
                logging.info(test_def.prompt)

                if err_msg is None: exit_test = handle_user_prompt(test_def)

            #Automatic test
            else:
                err_msg = test_def.func()
                test_res = "passed" if err_msg is None else "failed"
                logging.info("Testing {:s}: {:s}".format(test_def.name, test_res))

            if err_msg is not None:
                exit_test = True
                logging.error(err_msg)

            if exit_test: test_index = len(test_seq)
            else: test_index += 1

        test_res = f"{tc.green}PASS" if not exit_test else f"{tc.red}FAIL"

        logging.info(f"Board test complete, result is {test_res}{tc.rst}\n")

        time.sleep(2)
        logging.info("Unload current PCBA and hit enter")
        input()

        initialize()
        brd_num += 1

if __name__ == "__main__":
    blower_main()
