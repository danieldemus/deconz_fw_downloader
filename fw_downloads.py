#!/usr/bin/env python3
"""
Snipped to download current IKEA ZLL OTA files into ~/otau
compatible with python 3.
"""
import argparse
import datetime

from danfoss import Danfoss
from ikea import Ikea
from github_koenkk import GithubKoenkk
from ligthify import Lightify

parser = argparse.ArgumentParser(
    prog = 'fw_downloads.py',
    description = 'Downloads zigbee firmware update files from various sources for the Deconz OTA plugin')
parser.add_argument('-v', '--verbose', action='store_true', help='write each file operation to the console')
args = parser.parse_args()

print ('%s - Downloadscript started' % f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")

Danfoss(args.verbose).perform_downloads()
Ikea(args.verbose).perform_downloads()
GithubKoenkk(args.verbose).perform_downloads()
Lightify(args.verbose).perform_downloads()

print ('%s - Downloadscript finished' % f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
