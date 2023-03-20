import json
import logging
import os
import sys
import time

import pygtail

ERR_FILE_NOT_FOUND = 1


def follow(file, skip_existing_data=False, sleep_sec=0.5):
    """
    Generator that indefinitely follows a file and yields new lines as they are added.

    This function uses the Pygtail library to handle parsing and resuming from the previous session,
    simplifying the process of following files. When the file is updated, the generator yields new lines.

    Parameters:
        file (str): The path to the file to follow.
        skip_existing_data (bool, optional): If True, the function will skip the existing contents of
            the file and only yield new lines added after the generator is created. Defaults to False.
        sleep_sec (float, optional): The time interval, in seconds, to wait before checking for updates
            to the file when no new lines are available. Defaults to 0.5.

    Yields:
        str: New lines appended to the file.

    Raises:
        SystemExit: If the specified file is not found.
    """
    try:
        last_mod = os.path.getmtime(file)
    except FileNotFoundError:
        logging.error("Log file at %s not found!", file)
        sys.exit(ERR_FILE_NOT_FOUND)

    while True:
        # if there is any content, this block is run
        for line in pygtail.Pygtail(str(file)):
            if not skip_existing_data:
                yield line
        # when there is nothing left to read, wait for change in file
        while last_mod == os.path.getmtime(file):
            time.sleep(sleep_sec)
        last_mod = os.path.getmtime(file)
        continue

def get_visitor_id_from_log_line(line: str):
    entry = json.loads(line.strip())
    if 'request' in entry:
        return entry['request']['remote_ip']
    return 'unknown'
