#!/usr/bin/env python3
"""
Snipped to download current IKEA ZLL OTA files into ~/otau
compatible with python 3.
"""

import datetime

from danfoss import Danfoss
from ikea import Ikea
from github_koenkk import GithubKoenkk
from ligthify import Lightify

print ('%s - Downloadscript started' % f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")

Danfoss().perform_downloads()
Ikea().perform_downloads()
GithubKoenkk().perform_downloads()
Lightify().perform_downloads()

print ('%s - Downloadscript finished' % f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
