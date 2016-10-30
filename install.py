from __future__ import print_function
import argparse
import json
import logging
import os
import subprocess
import sys
import csv
import urllib
import zipfile
from sys import platform as _platform
import time
import shutil
import requests
from datetime import datetime
import utils

# TODO: Rearrange directories for a proper import
CURR_DIR = os.path.dirname(os.path.realpath(__file__))
GTAV_DIR = os.environ['GTAV_DIR']
SAVED_GAMES_LOCATION = os.path.expanduser('~\\Documents\\Rockstar Games\\GTA V\\Profiles\\')

logger = logging.getLogger(__name__)


def get_saved_games_profile_folders():
    profiles = os.listdir(SAVED_GAMES_LOCATION)
    if len(profiles) > 1:
        print('More than one GTAV settings profile found, replacing saved games of all profiles')
    elif len(profiles) == 0:
        print('No GTAV settings profile found to load saved games into. Aborting')
        exit(1)
    return [SAVED_GAMES_LOCATION + profile for profile in profiles]


def setup():
    replace_saved_games()
    utils.download_folder('https://www.dropbox.com/sh/fy6nha3ikm2ugij/AADm8SPKm5bX3Nl2qx69rCcYa?dl=1', GTAV_DIR)


def replace_saved_games():
    # TODO: Make a backup copy to a timestamped folder in '~\\Documents\\GTAV_saved_games_backup_%timestamp%'
    saved_games_profile_folders = get_saved_games_profile_folders()
    location = urllib.urlretrieve('https://www.dropbox.com/sh/k1osqcufsubo754/AADCeXM4I1iYRz19bdO12pOba?dl=1')
    location = location[0]
    zip_ref = zipfile.ZipFile(location, 'r')
    backup_saved_games()
    for saved_games_location in saved_games_profile_folders:
        print('Replacing saved games in', saved_games_location)
        zip_ref.extractall(saved_games_location)
    zip_ref.close()


def backup_saved_games():
    time_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_location = os.path.expanduser('~\\Documents\\GTAV_saved_games_backup_' + time_str)
    print('Backing up saved games in %s to %s' % (SAVED_GAMES_LOCATION, backup_location))
    shutil.copytree(SAVED_GAMES_LOCATION, backup_location)


def main():
    parser = argparse.ArgumentParser(description=None)
    args = parser.parse_args()
    logging.basicConfig()
    logger.setLevel(logging.INFO)
    setup()


if __name__ == '__main__':
    sys.exit(main())
