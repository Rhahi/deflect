import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict
from zoneinfo import ZoneInfo

import pygtail

CWD = Path(os.getcwd())
VISITOR_FILE = CWD / 'visitor'
LOG_FILE = CWD / 'access.log'
UPDATE_PERIOD = 300
TZ = 'Europe/Stockholm'

def today():
    tz = ZoneInfo(TZ)
    return datetime.now(tz).isoformat()

def update_file(unique, total, newline=False):
    # find previous information or create new
    try:
        with open(VISITOR_FILE, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        with open(VISITOR_FILE, 'w') as f:
            lines = []
    if len(lines) == 0:
        newline = True
    # write a new line
    if newline:
        with open(VISITOR_FILE, 'a') as f:
            f.write(f'{today()} {unique} {total}\n')
    # or modify the last line
    else:
        with open(VISITOR_FILE, 'r+') as f:
            f.seek(0)
            for line in lines[:-1]:
                f.write(line)
            last_line = lines[-1].strip()
            timestamp, _, _ = last_line.split()
            f.write(f'{timestamp} {unique} {total}\n')
            f.truncate()

def read_visitor():
    """load visitor count from previous session"""
    try:
        with open(VISITOR_FILE, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1].strip()
                _, unique, total = last_line.split()
                return int(unique), int(total)
            else:
                return 0, 0
    except FileNotFoundError:
        return 0, 0

def update_buffer(buffer: Dict, visitor, unique: int, total: int):
    """update internal unique visior memory and return up to date number"""
    total += 1
    if visitor in buffer:
        buffer[visitor] += 1
    else:
        buffer[visitor] = 1
        unique += 1
    logging.info("unique: %i, total: %i", unique, total)
    return unique, total

def seconds_since_last_save(file_path):
    return time.time() - os.path.getmtime(file_path)

def get_visitor_from_entry(entry: Dict):
    if 'request' in entry:
        return entry['request']['remote_ip']
    else:
        logging.warning("got an unknown entry")
        logging.warning(entry)
        return 'unknown'

def is_new_day(prev: datetime):
    now = datetime.now()
    if now.day > prev.day and now.hour >= prev.hour:
        return True
    return False

def follow(file, sleep_sec=0.5):
    last_mod = os.path.getmtime(file)
    while True:
        # pygtail takes care of continue parseing from prev session
        for line in pygtail.Pygtail(str(file)):
            yield line
        else:
            # polling method
            while last_mod == os.path.getmtime(file):
                time.sleep(sleep_sec)
            last_mod = os.path.getmtime(file)
            continue

def main():
    unique, total = read_visitor()
    buffer = {}
    last_day = datetime.now()
    first_load = True
    try:
        for line in follow(LOG_FILE):
            # parse and process
            logging.debug("processing line")
            visitor = get_visitor_from_entry(json.loads(line.strip()))
            if visitor == 'unknown':
                continue
            # update internal
            unique, total = update_buffer(buffer, visitor, unique, total)
            last_day = main_update(first_load, last_day, unique, total)
    except KeyboardInterrupt:
        main_update(first_load, last_day, unique, total)

def main_update(first_load: bool, last_day: datetime, unique: int, total: int):
    if first_load or (seconds_since_last_save(VISITOR_FILE) > UPDATE_PERIOD):
        first_load = False
        if is_new_day(last_day):
            logging.debug("update (newline)")
            update_file(unique, total, newline=True)
        else:
            logging.debug("update (modify)")
            update_file(unique, total, newline=False)
    return datetime.now()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
