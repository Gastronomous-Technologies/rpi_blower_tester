from subprocess import run
import os

from .blower_main import blower_main

run("cls" if os.name == 'nt' else "clear", shell=True)

blower_main()