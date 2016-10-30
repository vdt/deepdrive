#!/usr/bin/python
from __future__ import print_function

import os
import sys
import urllib
import zipfile

import requests


def download_file(url, path):
    """Good for downloading large files from dropbox as it sets gzip headers and decodes automatically on download"""
    with open(path, "wb") as f:
        print('Downloading', url)
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None:  # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()


def download_folder(url, path):
    """Useful for downloading a folder as a zip from dropbox and unzipping it to path"""
    print('Downloading', url)
    location = urllib.urlretrieve(url)
    location = location[0]
    zip_ref = zipfile.ZipFile(location, 'r')
    print('Unzipping', location, 'to', path)
    zip_ref.extractall(path)
    zip_ref.close()
    os.remove(location)
