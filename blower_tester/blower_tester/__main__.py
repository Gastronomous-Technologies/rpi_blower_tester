from subprocess import run
import os
import argparse
import logging

from .blower_main import blower_main
from .config import conf

parser = argparse.ArgumentParser(prog="Blower Tester",
description="Testing application for CG6-CHAS-E-019 with tester CG6-TEST-E-019",
    epilog="Supports CG6-CHAS-E-019 v1.5+")

parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

log_level = logging.DEBUG if args.verbose else logging.INFO

logging.basicConfig(format="%(levelname)s:      %(message)s",
                    datefmt='%s', level=log_level)

blower_main()