#!/usr/bin/env python3
import json
from urllib.request import urlopen

from downloader import Downloader

class Ikea(Downloader):

    def getUrlList(self):
                
        f = urlopen("http://fw.ota.homesmart.ikea.net/feed/version_info.json")
        data = f.read()

        arr = json.loads(data)
        res = []
        for i in arr:
            if 'fw_binary_url' in i:
                url = i['fw_binary_url']
                ls = url.split('/')
                fname = ls[len(ls) - 1]

                res.append((url, fname))

        return res


