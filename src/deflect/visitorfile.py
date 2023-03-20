import logging
import os
import sys
import time
from dataclasses import dataclass, replace
from datetime import datetime, timedelta

ERR_FILE_NOT_FOUND = 1


@dataclass
class VisitorStat:
    date: datetime = datetime.now().replace(microsecond=0)
    today_unique_visitors: int = 0
    today_total_visitors: int = 0
    unique_visitors: int = 0
    total_visitors: int = 0

    def __repr__(self):
        date = self.date.replace(microsecond=0).isoformat()
        tuv = self.today_unique_visitors
        ttv = self.today_total_visitors
        uv = self.unique_visitors
        tv = self.total_visitors
        return f"{date},{tuv},{ttv},{uv},{tv}"

def create_visitorfile(file):
    if os.path.isfile(file):
        logging.info("visitorfile already exists")
        with open(file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 3:
            logging.info("Continuing from previous visitorfile")
            return
    logging.info("Creating a new visitorfile")
    with open(file, "w", encoding="utf-8") as f:
        f.write("<html><head><title>Visitor stats</title></head><body>\n")
        f.write("timestamp,today_unique_visitors,today_total_visitors,total_visitors,unique_visitors,<br />\n")
        f.write("</body><html>\n")

def read_visitorfile(file):
    line = _read_last_line(file)
    if line is None:
        return None
    data = line.split(",")
    date = datetime.fromisoformat(data[0])
    numbers = tuple(map(int, data[1:5]))
    return VisitorStat(date, *numbers)

def write_visitorfile(file, data: VisitorStat, write_schedule: datetime):
    """
    Update the visitor data in a file by modifying the last line or appending a new line.

    This function modifies the last line of the file if the current time is before the
    scheduled time. If the current time is greater than or equal to the scheduled time,
    it appends a new line to the file and updates the write_schedule for the next day.
    The write_schedule is always calculated using the current date and the given schedule's time.

    Args:
        file: The path to the file to be modified.
        data (VisitorStat): The visitor data to be written to the file.
        write_schedule (datetime): The datetime object representing the scheduled time
                                   for appending a new line.

    Returns:
        datetime: The updated write_schedule for the next day.
    """
    now = datetime.now()
    if now > write_schedule:
        logging.debug("appending to visitorfile")
        _update_last_line(file, str(data), append=True)
        next_day = now.date() + timedelta(days=1)
        return datetime.combine(next_day, write_schedule.time())
    logging.debug("updating visitorfile")
    _update_last_line(file, str(data), append=False)
    return write_schedule

def _read_last_line(file, skip_head=2, skip_tail=1):
    """
    Open a visitorfile and return the content of the last body line.

    Returns:
        str or None: The content of the last line of the file as a string,
        or None if the file is empty.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the user does not have permission to read the file.
    """
    with open(file, "r", encoding='utf-8') as f:
        lines = f.readlines()
        if len(lines) < skip_head + skip_tail:
            raise ValueError("Given file does not satisfy skip conditions")
        if len(lines) == skip_head + skip_tail:
            return None
        return lines[-(skip_tail+1)]

def _update_last_line(file, text: str, append=True, skip_head=2, skip_tail=1):
    """
    Open a visitorfile and overwrite the last body with the given text.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the user does not have permission to modify the file.
    """
    if not os.path.isfile(file):
        raise FileNotFoundError
    text = text + ",<br />\n"
    with open(file, "r", encoding='utf-8') as f:
        lines = f.readlines()
    if len(lines) < skip_head + skip_tail:
        raise ValueError("Given file does not satisfy skip conditions")
    if len(lines) == skip_head + skip_tail:
        append = True
    if append:
        lines.insert(len(lines)-1, text)
    else:
        lines[len(lines)-2] = text
    with open(file, "w", encoding='utf-8') as f:
        f.writelines(lines)

def update_stat(
    daily_tracker: dict,
    total_tracker: dict,
    visitor: str,
    data: VisitorStat
):
    """
    Update the internal unique visitor memory and return an up-to-date VisitorStat dataclass.

    Args:
        daily_tracker (dict): The tracker containing unique daily visitor id.
        total_tracker (dict): The tracker containing unique visitor id.
        visitor (str): The visitor id to be recorded in the tracker.
        data (VisitorStat): The current VisitorStat data.

    Returns:
        VisitorStat: The updated VisitorStat dataclass.
    """

    if visitor not in total_tracker:
        # bump all
        daily_tracker[visitor] = 1
        total_tracker[visitor] = 1
        return replace(
            data,
            today_unique_visitors=data.today_unique_visitors + 1,
            today_total_visitors=data.today_total_visitors + 1,
            unique_visitors=data.unique_visitors + 1,
            total_visitors=data.total_visitors + 1,
        )
    if visitor not in daily_tracker:
        # bump just daily
        daily_tracker[visitor] = 1
        total_tracker[visitor] += 1
        return replace(
            data,
            today_unique_visitors=data.today_unique_visitors + 1,
            today_total_visitors=data.today_total_visitors + 1,
            total_visitors=data.total_visitors + 1,
        )
    # bump totals only
    daily_tracker[visitor] += 1
    total_tracker[visitor] += 1
    return replace(
        data,
        today_total_visitors=data.today_total_visitors + 1,
        total_visitors=data.total_visitors + 1,
    )

def seconds_since_last_save(file):
    """Check modified date of a file and return seconds since last modify"""
    try:
        return time.time() - os.path.getmtime(file)
    except FileNotFoundError:
        logging.error("Log file at %s not found!", file)
        sys.exit(ERR_FILE_NOT_FOUND)
