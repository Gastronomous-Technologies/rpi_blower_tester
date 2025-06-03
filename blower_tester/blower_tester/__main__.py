import time
from subprocess import run

from os import getlogin

run("clear", shell=True)
print("hello from the container")
time.sleep(10)
