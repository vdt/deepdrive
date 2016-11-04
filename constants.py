import os
from datetime import datetime

try:
   input = raw_input
except NameError:
   pass

DEEP_DRIVE_CONFIG_LOCATION = os.path.expanduser('~\\AppData\\Roaming\\DeepDrive\\config.json')
GTAV_DIR = os.environ['GTAV_DIR']
SAVED_GAMES_LOCATION = os.path.expanduser('~\\Documents\\Rockstar Games\\GTA V\\Profiles\\')
IS_STEAM = 'steam' in GTAV_DIR.lower()

AUTOIT_PROCESS_NAME = 'AutoItX.exe'
OBS_PROCESS_NAME = 'OBS.exe'
GTAV_PROCESS_NAME = 'GTA5.exe'
CAFFE_PROCESS_NAME = 'caffeout.exe'
INSTALL_TIME_STR = datetime.now().strftime('%Y%m%d_%H%M_%S')
