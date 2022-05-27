#!/usr/bin/env python3
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import os, requests, re, time
import tempfile
import shutil

class Downloader(ABC):

    extensions = ('.ota', '.ota.signed', '.zigbee', '.fw2', '.sbl-ota')
    
    def __init__(self):
        self.otauPath = os.path.expanduser('~/otau')

    @abstractmethod
    def getUrlList(self):
        pass

    def performDownloads(self):
        print("")
        print(f"Putting {self.__class__.__name__} updates in {self.otauPath}")
        if not os.path.exists(self.otauPath):
            os.makedirs(self.otauPath)

        cnt = 0
        retries = self.getUrlList()
        delay = None
        while cnt == 0 or (cnt < 50 and delay):
            retries, delay = self.handleDownloads(retries, delay)
            cnt += 1

    def handleDownloads(self, lst, delay):
        retries = []

        if delay:
            nowish = datetime.now(timezone.utc) + timedelta(seconds=-2)
            if delay > nowish:
                wait = (delay - nowish).seconds + 1
                print(f"Some downloads were deferred by the server. Waiting {wait} seconds until retry", end='', flush=True)
                ix = 0
                while ix < wait:
                    print('.', end='', flush=True)
                    ix += 1
                    time.sleep(1)
                print("", flush=True)

        newDelay = None

        for (url, filename) in lst:
            ret = self.downloadFile(url, filename, retries)
            if ret is None or isinstance(ret, datetime):
                if ret is not None or newDelay is None or ret > newDelay:
                    newDelay = ret
                continue

            fname, firmwarecontent = ret
            self.handleContent(fname, firmwarecontent)
        return retries, newDelay

    def downloadFile(self, url, filename, retries):
        if filename and os.path.isfile(os.path.join(self.otauPath, filename)):
            print(f"{filename} skipped. A file with that name already exists")
            return None

        response = requests.get(url)
        if 'Retry-After' in response.headers:
            timestamp = parsedate_to_datetime(response.headers['Date'])
            delay = timedelta(seconds=int(response.headers['Retry-After']) + 1)
            retries.append((url, filename))
            return timestamp + delay

        fname: str = filename

        if 'Content-Disposition' in response.headers:
            contentDisposition = response.headers['Content-Disposition']
            contentDisposition = re.findall("filename=(.+)", contentDisposition)[0]
            contentDisposition = contentDisposition.split(";")
            fname = contentDisposition[0]

        return fname, response.content

    def handleContent(self, fname, firmwarecontent):
        if fname.endswith(self.extensions):
            fullname = os.path.join(self.otauPath, fname)

            if not os.path.isfile(fullname):
                file = open(fullname, "wb")
                file.write(firmwarecontent)
                file.close()
                print(f"{fname} downloaded")
            else:
                print(f"{fname} skipped. A file with that name already exists")
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                fullname = os.path.join(tmpdirname, fname)

                if not os.path.isfile(fullname):
                    file = open(fullname, 'wb')
                    file.write(firmwarecontent)
                    file.close()
                    
                shutil.unpack_archive(fullname, tmpdirname)
                print(f"Downloaded and unpacked {fname}")
                for f in self.filteredFilelist(tmpdirname):
                    target = os.path.join(self.otauPath, os.path.basename(f))
                    if not os.path.isfile(target):
                        shutil.copyfile(f, target)
                        print('Extracted %s' % os.path.basename(f))
                    else:
                        print('%s skipped. A file with that name already exists' % os.path.basename(f))

    def filteredFilelist(self, rootDir):
        return [os.path.join(r, fn)
                for r, ds, fs in os.walk(rootDir)
                for fn in fs if fn.endswith(self.extensions)]
