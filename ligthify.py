#!/usr/bin/env python3

import requests, json, time
from downloader import Downloader

class Lightify(Downloader):

    def get_url_list(self):
        response = requests.get("https://api.update.ledvance.com/v1/zigbee/products")
        if 'Retry-After' in response.headers:
            defer = int(response.headers['Retry-After']) + 1
            print(f"Waiting {defer} seconds to get ledvance list")
            time.sleep(defer)
            response = requests.get("https://api.update.ledvance.com/v1/zigbee/products")

        response = json.loads(response.content)

        productlist = response['products']
        res = []
        for x in productlist:
            company = x.get('id').get('company')
            product = x.get('id').get('product')
            res.append(('https://api.update.ledvance.com/v1/zigbee/firmwares/download/%s/%s/latest' % (company, product), None))

        return res
