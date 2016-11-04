from __future__ import print_function

import time
import os
import glob
from threading import Thread


def follow(log_file):
    log_file.seek(0, 2)  # Go to the end of the file
    while True:
        line = log_file.readline()
        if not line:
            time.sleep(0.1)  # Sleep briefly
            continue
        yield line


def tail_log(log_file_name):
    logfile = open(log_file_name)
    loglines = follow(logfile)
    for line in loglines:
        print('caffe:', line.rstrip())


def tail_caffe_logs():
    log_path = os.path.expanduser("~/appdata/local/temp/")
    newest = max(glob.iglob(log_path + 'caffe*log*'), key=os.path.getctime)
    thread = Thread(target=tail_log, args=(newest,))
    thread.setDaemon(True)
    thread.start()
    return thread


if __name__ == '__main__':
    thread = tail_caffe_logs()
    thread.join()
