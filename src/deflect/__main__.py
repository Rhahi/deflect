import logging
import dataclasses
import argparse
import sys
from datetime import datetime

from deflect import logfile, visitorfile


def main(config: dict):
    visitorfile.create_visitorfile(config["visitorfile"])
    data = visitorfile.read_visitorfile(config["visitorfile"]) or visitorfile.VisitorStat()
    tracker_daily = {}
    tracker_total = {}
    first_load = True
    write_schedule = config["newline-hour"]
    try:
        for line in logfile.follow(config["logfile"]):
            logging.debug("Processig new entry")
            visitor = logfile.get_visitor_id_from_log_line(line)
            if visitor == "unknown":
                logging.warning("Ignored an unparsable line: %s", line)
                continue
            data = visitorfile.update_stat(tracker_daily, tracker_total, visitor, data)
            # periodically render results
            if first_load or (visitorfile.seconds_since_last_save(config["logfile"]) >= config["update_interval"]):
                new_schedule = visitorfile.write_visitorfile(config["visitorfile"], data, write_schedule)
                # reset daily counter
                if new_schedule != write_schedule:
                    logging.info("Resetting daily counter -- %s", data)
                    tracker_daily = {}
                    data = dataclasses.replace(data, today_unique_visitors=0, today_total_visitors=0)
                    write_schedule = new_schedule
    except KeyboardInterrupt:
        # final save before exiting
        visitorfile.write_visitorfile(config["visitorfile"], data, write_schedule)

def get_config():
    parser = argparse.ArgumentParser(description="Visitor tracking and logging")
    parser.add_argument(
        "-f", "--visitorfile",
        type=str,
        default="./visitorfile.html",
        help="Path to the visitor file (specialized HTML file)",
    )
    parser.add_argument(
        "-l", "--logfile",
        type=str,
        default="./access.log",
        help="Path to the log file from Caddy",
    )
    parser.add_argument(
        "-n", "--newline-hour",
        type=int,
        choices=range(0,24),
        default=datetime.now().hour,
        help="Scheduled time for starting a new day",
    )
    parser.add_argument(
        "-i", "--update-interval",
        type=int,
        default=120,
        help="Update interval in seconds",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable logging output",
    )
    parser.add_argument(
        "-vv", "--verbose-debug",
        action="store_true",
        help="Enable more verbose logging output",
    )
    args = parser.parse_args()
    return {
        "visitorfile": args.visitorfile,
        "logfile": args.logfile,
        "newline-hour": datetime.now().replace(hour=args.newline_hour),
        "update-interval": args.update_interval,
        "verbose": args.verbose,
        "verbose-debug": args.verbose_debug,
    }

if __name__ == "__main__":
    conf = get_config()
    FORMAT = '\033[32m[%(levelname)s] %(asctime)s: %(message)s\033[0m'
    if conf["verbose-debug"]:
        logging.basicConfig(format=FORMAT, level=logging.DEBUG)
        logging.debug("Log level: Debug")
    elif conf["verbose"]:
        logging.basicConfig(format=FORMAT, level=logging.INFO)
        logging.info("Log level: info")
    main(conf)
