#!/usr/bin/python
import argparse
import json
import logging
import os
import subprocess
import sys
import csv
import traceback
import urllib
import urllib2
import zipfile
from sys import platform as _platform
import time

import utils
from constants import *
from enforce_version import enforce_version


# make AMI's for every region

# remove steam password
# reset system password on restart
from tail_logs import tail_caffe_logs

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)


ALL_PROCESS_NAMES = [CAFFE_PROCESS_NAME, AUTOIT_PROCESS_NAME, GTAV_PROCESS_NAME]


def _start_gtav_command(_install_dir):
    if IS_STEAM:
        start_command = r'start steam://rungameid/271590'
    else:
        start_command = r'"{GTAV_DIR}/PlayGTAV.exe"'.format(GTAV_DIR=GTAV_DIR)
    return start_command


def _start_obs_command(install_dir):
    return r'"{install_dir}/OBS-new/rundir/OBS.exe"'.format(install_dir=install_dir)


def _start_autoit_command(install_dir):
    return r'"{install_dir}/AutoIt3/AutoItX/AutoItX.exe"'.format(install_dir=install_dir)


def _gtav_is_running():
    p_tasklist = subprocess.Popen('tasklist.exe /fo csv',
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True)

    pythons_tasklist = []
    tasks = list(csv.DictReader(p_tasklist.stdout))
    for p in tasks:
        if p['Image Name'] == GTAV_PROCESS_NAME:
            pythons_tasklist.append(p)
    if len(pythons_tasklist) > 0:
        return True
    else:
        return False


class GTAVRunner(object):
    def __init__(self, install_dir, weights_path):
        self.install_dir = install_dir
        self.weights_path = weights_path
        self.gtav_process = None
        self.obs_process = None
        self.caffe_process = None
        self.autoit_process = None
        self.processes = []

    def _configure(self):
        self.popen()

    def _start_process(self, proc_name, get_cmd_fn, shell=True, cwd=None):
        cmd = get_cmd_fn(self.install_dir)
        logger.info(r'Starting {proc_name} with the following command: {cmd}'.format(proc_name=proc_name, cmd=cmd))
        process = subprocess.Popen(cmd, shell=shell, cwd=cwd)
        self.processes.append(process)
        return process

    def popen(self):
        self._kill_competing_procs()
        self.obs_process = self._start_process('OBS', _start_obs_command)
        input('Press any key after ensuring GTAV is not open and hitting the "Preview Stream" button in OBS...')
        self.gtav_process = self._start_process('GTAV', _start_gtav_command)
        if IS_STEAM:
            steam_message = ' (you may need to login to steam as well)'
        else:
            steam_message = ''
        input('Start in normal mode if asked, then press any key after entering story mode %s, loading Franlkin and Lamar saved game from 5/14/16, and making sure the camera is on the hood (see the setup readme for more details)...' % steam_message)
        caffe_work_dir = self.install_dir + '/caffe'
        self.caffe_process = self._start_process('Caffe', self._start_caffe_command, shell=False, cwd=caffe_work_dir)
        self.autoit_process = self._start_process('AutoIt', _start_autoit_command, shell=False)
        pass

    def _start_caffe_command(self, install_dir):
        return [r'{install_dir}/caffe/build/x64/Release/caffeout.exe'.format(install_dir=install_dir), self.weights_path]

    @staticmethod
    def _kill_competing_procs():
        subprocess.call("taskkill /IM %s /F" % OBS_PROCESS_NAME)
        subprocess.call("taskkill /IM %s /F" % AUTOIT_PROCESS_NAME)
        subprocess.call("taskkill /IM %s /F" % CAFFE_PROCESS_NAME)
        subprocess.call("taskkill /IM %s /F" % GTAV_PROCESS_NAME)
        subprocess.call("taskkill /IM GTAV* /F")
        subprocess.call("taskkill /IM Steam* /F")

    def popen_cleanup(self):
        for proc in self.processes:
            proc.kill()
            proc.wait()

        # Kill procs that we might have missed
        self._kill_competing_procs()


def main():
    default_weights_path = 'caffe_deep_drive_train_iter_35352.caffemodel'
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-v', '--verbose', action='count', dest='verbosity', default=0, help='Set verbosity.')
    parser.add_argument('-w', '--weights', default=default_weights_path, help='Path to caffemodel weights file - default is ' + default_weights_path)
    args = parser.parse_args()

    logging.basicConfig()

    if args.verbosity == 0:
        logger.setLevel(logging.INFO)
    elif args.verbosity >= 1:
        logger.setLevel(logging.DEBUG)

    GTAVRunner._kill_competing_procs()

    enforce_version(GTAV_DIR)

    install_dir = utils.get_config()['install_dir']

    runner = GTAVRunner(install_dir, args.weights)
    runner.popen()
    time.sleep(10)  # Give some time for caffe to create a new log file
    tail_caffe_logs()
    while True:
        if utils.processes_are_running(ALL_PROCESS_NAMES):
            if 'GTAV_DEAD_MANS_SNITCH_URL' in os.environ:  # i.e. https://nosnch.in/a69389848a
                # Send heartbeat (for monitoring long running environments)
                logging.info('Sending heartbeat')
                try:
                    urllib2.urlopen(os.environ['GTAV_DEAD_MANS_SNITCH_URL']).read()
                except Exception as e:
                    logging.error('Error sending heartbeat \n' + traceback.format_exc())
        time.sleep(15 * 60)

if __name__ == '__main__':
    sys.exit(main())
