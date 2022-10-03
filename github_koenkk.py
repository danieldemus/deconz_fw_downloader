#!/usr/bin/env python3

from posixpath import basename
import requests, json, time
from downloader import Downloader

class GithubKoenkk(Downloader):

    def get_url_list(self):
        res = []
        response = requests.get('https://raw.githubusercontent.com/Koenkk/zigbee-OTA/master/index.json')
        data = json.loads(response.content)

        for x in data:
            url = x['url']
            if 'path' in x:
                filename = basename(x['path'])
            else:
                filename = basename(url)
            res.append((url, filename))

        return res
