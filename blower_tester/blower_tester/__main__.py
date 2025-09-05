from subprocess import run
import os
import argparse
import logging

from .blower_main import blower_main
from .config import conf

parser = argparse.ArgumentParser(prog="Blower Tester",
description="Testing application for CG5-ELEC-E-019 with tester CG5-TEST-E-019",
    epilog="Supports CG5-ELEC-E-019 v2.1+")

parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

log_level = logging.DEBUG if args.verbose else logging.INFO

logging.basicConfig(format="%(levelname)s:      %(message)s",
                    datefmt='%s', level=log_level)

blower_main()
