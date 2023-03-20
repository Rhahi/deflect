import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

from deflect.logfile import follow

def test_follow_wait_for_new_data():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        f.write("Line 1\n")
        f.write("Line 2\n")
        f.write("Line 3\n")
        temp_file_path = f.name

    try:
        gen = follow(temp_file_path)

        assert next(gen) == "Line 1\n"
        assert next(gen) == "Line 2\n"
        assert next(gen) == "Line 3\n"

        def append_new_data():
            time.sleep(0.5)
            with open(temp_file_path, "a", encoding='utf-8') as f:
                f.write("Line 4\n")

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(append_new_data)
            assert next(gen) == "Line 4\n"
            future.result()

    finally:
        os.remove(temp_file_path)

def test_follow_existing_file_without_contents():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        temp_file_path = f.name

    try:
        gen = follow(temp_file_path)

        with open(temp_file_path, "a", encoding='utf-8') as f:
            f.write("Line 1\n")

        assert next(gen) == "Line 1\n"
    finally:
        os.remove(temp_file_path)
