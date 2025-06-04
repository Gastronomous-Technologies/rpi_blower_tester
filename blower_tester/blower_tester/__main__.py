import logging
import time
from subprocess import run
import os
import RPi.GPIO as GPIO

from .config import pins
from .config import text_colour as tc

def disp_start_info():
    logging.info(f"{tc.bold}CG5-ELEC-E-019 BlowerThermocouple Tester{tc.rst}")
    logging.info("Supports Version v2.1+ PCBs\n")
    logging.info("Enter y (yes) to confirm and complete next test")
    logging.info("Enter n (no) to offer debug and retest")
    logging.info("Enter ? (unsure) to retest")
    logging.info("Enter e (exit) to exit test")
    logging.info("All prompts refer to the board under test\n")

def __initialize():
    logging.debug("Initializing GPIO pins")
  
    GPIO.mode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(pins.alert, GPIO.IN)

    GPIO.setup(pins.cs,  GPIO.OUT) 
    GPIO.setup(pins.pwr_en,  GPIO.OUT)

    GPIO.output(pins.cs, GPIO.HIGH)   
    GPIO.output(pins.pwr_en, GPIO.LOW)

def __pwr_on():
    logging.debug("Asserting power enable pin")
    GPIO.output(pins.pwr_en, GPIO.HIGH)
    
def blower_main():
    logging.basicConfig(format="%(levelname)s:      %(message)s", 
                        datefmt='%s', level=logging.INFO)
    
    run("cls" if os.name == 'nt' else "clear", shell=True)

    disp_start_info()
    __initialize()

    test_seq = [
        {"name": "power LEDs", "func": __pwr_on, "prompt": "Two leds on?", "auto": None, "debug": "for power shorts/opens"},   
    ]

    brd_num = 0

    while True:
        early_exit = False
        
        if brd_num == 0:
            logging.info("Press enter to test GOOD PCBA")
        else:
            logging.info("PCBA %d test".format(brd_num))

        res = input()
        
        test_index = 0
        while test_index < len(test_seq):          
            test_def = test_seq[test_index]

            logging.info("Testing %s: %s\n".format(test_def["name"], test_def["prompt"]))
 
            test_seq["func"]()
            res = input()

            while res != 'y' and test_index < len(test_seq):
                
                if(res == 'n'):
                    logging.error("Check %s\n", test_def["debug"])
                    time.sleep(2)

                elif((res == 'n') or res == '?'):
                    logging.info("\nTest %d: %s\n", test_index + 1, test_def["prompt"])
                    test_seq["func"]()
                
                elif(res == 'e'):
                    test_index = len(test_seq)
                    early_exit = True
                else:
                    logging.error("Unrecognized command, please try again...")

                res = input()
     
        test_res = f"{tc.green}pass" if not early_exit else f"{tc.red}fail"

        logging.info("\nBoard test complete, result is %s{tc.rst}\n\n".format(test_res)) 
        
        time.sleep(2)
        logging.info("Unload current PCBA\n")
        __initialize()
        brd_num += 1        
        time.sleep(5)

if __name__ == "__main__":
    blower_main()