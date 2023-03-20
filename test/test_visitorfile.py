import os
import tempfile
from datetime import datetime, timedelta

import pytest

from deflect.visitorfile import (VisitorStat, _read_last_line,
                                 _update_last_line, create_visitorfile,
                                 read_visitorfile, update_stat,
                                 write_visitorfile)


@pytest.fixture()
def vfile():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        file = f.name
    create_visitorfile(file)
    yield file
    os.remove(file)

def test_create(vfile):
    # get path for the test file
    assert os.path.isfile(vfile)
    with open(vfile, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert lines[0] == "<html><head><title>Visitor stats</title></head><body>\n"
    assert len(lines) == 3

def test_read_visitorfile_empty(vfile):
    assert read_visitorfile(vfile) is None

def test_write_visitorfile_1(vfile):
    data = VisitorStat()
    write_schedule = datetime.now()
    next_schedule = write_visitorfile(vfile, data, write_schedule)
    assert isinstance(next_schedule, datetime)
    assert read_visitorfile(vfile) == data

def test_write_visitorfile_2(vfile):
    data1 = VisitorStat(today_unique_visitors=1)
    data2 = VisitorStat(today_unique_visitors=2)
    data3 = VisitorStat(today_unique_visitors=3)
    schedule1 = datetime.now()

    # test append
    schedule2 = write_visitorfile(vfile, str(data1), schedule1)
    assert schedule2 - schedule1 >= timedelta(days=1)
    with open(vfile, "r", encoding="utf-8") as f:
        lines1 = f.readlines()
    assert len(lines1) == 4
    assert lines1[2] == str(data1) + ",<br />\n"

    # test re-write
    schedule3 = write_visitorfile(vfile, str(data2), schedule2)
    with open(vfile, "r", encoding="utf-8") as f:
        lines2 = f.readlines()
    assert schedule2 == schedule3
    assert len(lines2) == 4
    assert lines2[2] == str(data2) + ",<br />\n"

    # test append again
    write_visitorfile(vfile, str(data3), schedule1)
    with open(vfile, "r", encoding="utf-8") as f:
        lines3 = f.readlines()
    assert len(lines3) == 5
    assert lines3[2] == str(data2) + ",<br />\n"
    assert lines3[3] == str(data3) + ",<br />\n"

def test_read_visitor(vfile):
    data1 = VisitorStat(today_unique_visitors=1)
    schedule = datetime.now()
    write_visitorfile(vfile, str(data1), schedule)
    read_data = read_visitorfile(vfile)
    assert read_data.today_unique_visitors == 1
    assert read_data.today_total_visitors == 0
    assert read_data.total_visitors == 0
    assert read_data.unique_visitors == 0

def test_update():
    daily_tracker = {}
    total_tracker = {}
    initial_data = VisitorStat()

    # Test case 1: New visitor
    data = update_stat(daily_tracker, total_tracker, "visitor1", initial_data)
    assert data.today_unique_visitors == 1
    assert data.today_total_visitors == 1
    assert data.unique_visitors == 1
    assert data.total_visitors == 1

    # Test case 2: Repeating visitor
    data = update_stat(daily_tracker, total_tracker, "visitor1", data)
    assert data.today_unique_visitors == 1
    assert data.today_total_visitors == 2
    assert data.unique_visitors == 1
    assert data.total_visitors == 2

    # Test case 3: New visitor
    daily_tracker = {}  # Reset daily_tracker
    data = update_stat(daily_tracker, total_tracker, "visitor2", data)
    assert data.today_unique_visitors == 2
    assert data.today_total_visitors == 3
    assert data.unique_visitors == 2
    assert data.total_visitors == 3

def test_read_last_line():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("Line 0,<br />\n")
        f.write("Line 1,<br />\n")
        f.write("Line 2,<br />\n")
        f.write("Line 3,<br />\n")
        f.write("Line 4,<br />\n")
        temp_file_path = f.name
    try:
        assert _read_last_line(temp_file_path) == "Line 3,<br />\n"
    finally:
        os.remove(temp_file_path)

def test_update_last_line():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("Line 0,<br />\n")
        f.write("Line 1,<br />\n")
        f.write("Line 2,<br />\n")
        f.write("Line 3,<br />\n")
        f.write("Line 4,<br />\n")
        temp_file_path = f.name

    try:
        _update_last_line(temp_file_path, "New Last Line", append=False)
        with open(temp_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert lines[2] == "Line 2,<br />\n"
            assert lines[3] == "New Last Line,<br />\n"
    finally:
        os.remove(temp_file_path)

def test_update_last_line2():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("Line 0,<br />\n")
        f.write("Line 1,<br />\n")
        f.write("Line 2,<br />\n")
        temp_file_path = f.name
    try:
        _update_last_line(temp_file_path, "New Last Line", append=False)
        with open(temp_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 4
            assert lines[2] == "New Last Line,<br />\n"
            assert lines[3] == "Line 2,<br />\n"
    finally:
        os.remove(temp_file_path)

def test_update_last_line3():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("Line 0,<br />\n")
        f.write("Line 1,<br />\n")
        f.write("Line 2,<br />\n")
        f.write("Line 3,<br />\n")
        f.write("Line 4,<br />\n")
        temp_file_path = f.name
    try:
        _update_last_line(temp_file_path, "New Last Line", append=True)
        with open(temp_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 6
            assert lines[4] == "New Last Line,<br />\n"
            assert lines[5] == "Line 4,<br />\n"
    finally:
        os.remove(temp_file_path)
