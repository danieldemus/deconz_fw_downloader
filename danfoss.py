#!/usr/bin/env python3

from urllib.request import urlopen
from lxml.html import parse

from downloader import Downloader

class Danfoss(Downloader):

    def getUrlList(self):
        res = []
        page = parse(urlopen('https://files.danfoss.com/download/Heating/Ally/')).getroot()
        page.make_links_absolute('https://files.danfoss.com/download/Heating/Ally/')
        for link in page.cssselect('a'):
            if "OTA" in link.text_content():
                res.append((link.get('href'), link.text_content()))

        return res

