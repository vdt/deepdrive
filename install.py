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
from enforce_version import enforce_version
import json
from constants import *

CURR_DIR = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)


def get_saved_games_profile_folders():
    profiles = os.listdir(SAVED_GAMES_LOCATION)
    if len(profiles) > 1:
        print('More than one GTAV settings profile found, replacing saved games of all profiles')
    elif len(profiles) == 0:
        print('No GTAV settings profile found to load saved games into. Aborting')
        exit(1)
    return [SAVED_GAMES_LOCATION + profile for profile in profiles]


def install_autoit(install_dir):
    logger.info('Installing DeepDrive AutoIT')
    utils.download_folder('https://www.dropbox.com/s/09mtrrr42putjty/AutoIt3.zip?dl=1', install_dir)


def install_caffe(install_dir):
    logger.info('Installing DeepDrive Caffe and Neural Net')
    utils.download_folder('https://www.dropbox.com/s/zt77lslfrmw28m4/caffe.zip?dl=1', install_dir)


def install_obs(install_dir):
    logger.info('Installing DeepDrive OBS')
    utils.download_folder('https://www.dropbox.com/s/v4p75gxyqy6t9pi/OBS-new.zip?dl=1', install_dir)


def install_stuff_that_goes_in_gtav_dir():
    logger.info('Installing ScriptHookV and XBOX360CE to GTAV directory')
    files_to_backup = ['dinput8.dll', 'NativeTrainer.asi', 'ScriptHookV.dll', 'x360ce_x64.exe']
    files_to_backup = [os.path.join(GTAV_DIR, fname) for fname in files_to_backup]
    for fname in files_to_backup:
        if os.path.isfile(fname):
            shutil.copy2(fname, '%s.%s.deepdrive_backup' % (fname, INSTALL_TIME_STR))
    utils.download_folder('https://www.dropbox.com/sh/fy6nha3ikm2ugij/AADm8SPKm5bX3Nl2qx69rCcYa?dl=1', GTAV_DIR)


def setup(config, args):
    install_dir = config['install_dir']
    if args.gtav_dir_only:
        install_stuff_that_goes_in_gtav_dir()
    else:
        install_stuff_that_goes_in_gtav_dir()
        replace_saved_games()
        enforce_version(GTAV_DIR)
        install_autoit(install_dir)
        install_caffe(install_dir)
        install_obs(install_dir)


def replace_saved_games():
    saved_games_profile_folders = get_saved_games_profile_folders()
    location = urllib.urlretrieve('https://www.dropbox.com/sh/k1osqcufsubo754/AADCeXM4I1iYRz19bdO12pOba?dl=1')
    location = location[0]
    zip_ref = zipfile.ZipFile(location, 'r')
    backup_saved_games()
    for saved_games_profile_folder in saved_games_profile_folders:
        logger.info('Replacing saved games in', saved_games_profile_folder)
        zip_ref.extractall(saved_games_profile_folder)
    zip_ref.close()


def backup_saved_games():
    backup_location = os.path.expanduser('~\\Documents\\GTAV_saved_games_backup_' + INSTALL_TIME_STR)
    logger.info('Backing up saved games in %s to %s' % (SAVED_GAMES_LOCATION, backup_location))
    shutil.copytree(SAVED_GAMES_LOCATION, backup_location)


def main():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-g', '--gtav-dir-only', action='store_true', help='Only install things into the gtav directory')
    args = parser.parse_args()
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    config = utils.get_config()

    if not config:
        default_install_dir = 'C:\\Program Files\DeepDrive'
        install_dir = input('Where would you like to install DeepDrive? (press enter for %s): ' % default_install_dir)
        install_dir = install_dir or default_install_dir
        logger.info('Installing to %s', install_dir)
        config = {'install_dir': install_dir}
        config_dir = os.path.dirname(DEEP_DRIVE_CONFIG_LOCATION)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        with open(DEEP_DRIVE_CONFIG_LOCATION, 'w+') as outfile:
            json.dump(config, outfile, indent=4, sort_keys=True)

    setup(config, args)


if __name__ == '__main__':
    sys.exit(main())
