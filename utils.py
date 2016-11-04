#!/usr/bin/python
from __future__ import print_function

import csv
import json
import os
import subprocess
import sys
import urllib
import zipfile
import shutil
import errno
import requests

from constants import *


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
    """Useful for downloading a folder / zip file from dropbox and unzipping it to path"""
    print('Downloading', url)
    location = urllib.urlretrieve(url)
    location = location[0]
    zip_ref = zipfile.ZipFile(location, 'r')
    print('Unzipping', location, 'to', path)
    try:
        zip_ref.extractall(path)
    except Exception:
        print('You may want to close all programs that may have these files open or delete existing '
              'folders this is trying to overwrite')
        raise
    finally:
        zip_ref.close()
        os.remove(location)


def get_config():
    if os.path.isfile(os.path.join(DEEP_DRIVE_CONFIG_LOCATION)):
        with open(DEEP_DRIVE_CONFIG_LOCATION, 'r') as infile:
            return json.load(infile)


def processes_are_running(expected):
    expected = set(expected)
    actual = subprocess.Popen('tasklist.exe /fo csv', stdout=subprocess.PIPE, universal_newlines=True)
    actual = list(csv.DictReader(actual.stdout))
    actual = [p['Image Name'] for p in actual]
    intersection = set(actual).intersection(expected)
    ret = intersection == expected
    return ret