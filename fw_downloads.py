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
parser.add_argument('targets', help='Only download from the given targets. If none are specified, all will be tried', nargs='*', choices=['danfoss', 'ikea', 'lightify', 'koenkk'])
args = parser.parse_args()

print ('%s - Downloadscript started' % f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")

fetch_all = not args.targets

if fetch_all or 'koenkk' in args.targets:
    GithubKoenkk(args.verbose).perform_downloads()
if fetch_all or 'ikea' in args.targets:
    Ikea(args.verbose).perform_downloads()
if fetch_all or 'lightify' in args.targets:
    Lightify(args.verbose).perform_downloads()
if fetch_all or 'danfoss' in args.targets:
    Danfoss(args.verbose).perform_downloads()

print ('%s - Downloadscript finished' % f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
