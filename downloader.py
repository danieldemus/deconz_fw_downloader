#!/usr/bin/env python3
from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import os, requests, re, time
import tempfile
import shutil

class Downloader(ABC):

    extensions = ('.ota', '.ota.signed', '.zigbee', '.fw2', '.sbl-ota')
    archive_extensions = [ ext for sublist in [ x[1] for x in shutil.get_unpack_formats() ] for ext in sublist ]
    otau_path = os.path.join(os.path.expanduser('~/otau/'))
    log_path = os.path.join(otau_path, 'log.log')

    def __init__(self, verbose):
       self.verbose = verbose

    @abstractmethod
    def get_url_list(self):
        pass

    def perform_downloads(self):
        print("")
        print(f"Putting {self.__class__.__name__} updates in {self.otau_path}")
        if not os.path.exists(self.otau_path):
            os.makedirs(self.otau_path)

        cnt = 0
        retries = self.get_url_list()
        delay = None
        while cnt == 0 or (cnt < 50 and delay):
            retries, delay = self.handle_downloads(retries, delay)
            cnt += 1

    def handle_downloads(self, lst, delay):
        retries = []

        if delay:
            nowish = datetime.now(timezone.utc) + timedelta(seconds=-2)
            if delay > nowish:
                wait = (delay - nowish).seconds + 1
                if self.verbose:
                    print(f"Some downloads were deferred by the server. Waiting {wait} seconds until retry", end='', flush=True)
                ix = 0
                while ix < wait:
                    print('.', end='', flush=True)
                    ix += 1
                    time.sleep(1)
                print("", flush=True)

        newDelay = None

        for (url, filename) in lst:
            ret = self.download_file(url, filename, retries)
            if ret is None or isinstance(ret, datetime):
                if ret is not None or newDelay is None or ret > newDelay:
                    newDelay = ret
                continue

            fname, firmwarecontent = ret
            self.handle_content(fname, firmwarecontent, url)
        return retries, newDelay

    def download_file(self, url, filename, retries):
        if filename and os.path.isfile(os.path.join(self.otau_path, filename)):
            if self.verbose:
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

    def handle_content(self, fname: str, firmwarecontent, src: str):
        if fname.lower().endswith(self.extensions):
            fullname = os.path.join(self.otau_path, fname)

            if not os.path.isfile(fullname):
                file = open(fullname, "wb")
                file.write(firmwarecontent)
                file.close()
                print(f"{fname} downloaded")
                self.write_log(src, fname, len(firmwarecontent))
            else:
                if self.verbose:
                    print(f"{fname} skipped. A file with that name already exists")
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                fullname = os.path.join(tmpdirname, fname)

                if not os.path.isfile(fullname):
                    file = open(fullname, 'wb')
                    file.write(firmwarecontent)
                    file.close()
                if list(filter(lambda ext: fname.endswith(ext), self.archive_extensions)):
                    shutil.unpack_archive(fullname, tmpdirname)
                    if self.verbose:
                        print(f"Downloaded and unpacked {fname}")
                    for f in self.filtered_filelist(tmpdirname):
                        target = os.path.join(self.otau_path, os.path.basename(f))
                        if not os.path.isfile(target):
                            shutil.copyfile(f, target)
                            if self.verbose:
                                print(f"Extracted {os.path.basename(f)}")
                            self.write_log(fname, os.path.basename(f), os.path.getsize(f))
                        else:
                            if self.verbose:
                                print('%s skipped. A file with that name already exists' % os.path.basename(f))
                else:
                    print(f"{fname} is not a supported file type")

    def filtered_filelist(self, rootDir):
        return [os.path.join(r, fn)
                for r, ds, fs in os.walk(rootDir)
                for fn in fs if fn.endswith(self.extensions)]

    def write_log(self, src, fname, size):
        o = open(self.log_path, "at")
        o.write(src.ljust(100) + fname.ljust(50) + str(size).ljust(16))
        o.close()
