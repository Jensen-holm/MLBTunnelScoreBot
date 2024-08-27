#
# MLB Tunnel Bot
# Author: Jensen Holm
#

import MLBTunnelBot
import datetime
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def write_tweet(yesterday: datetime.date, debug: bool) -> None:
    try:
        tweet = MLBTunnelBot.write(yesterday=yesterday, debug=debug)
        logging.info(f"Successful write for {yesterday}\n{tweet}")
    except Exception as e:
        logging.error(f"Error for {yesterday} due to exception: {e.__class__} -> {e}")


def loop(yesterday: datetime.date, debug: bool) -> None:
    while True:
        next_iter_start_time = time.time() + (24 * 60 * 60) # 24 hours from now
        try:
            write_tweet(yesterday=yesterday, debug=debug)
        finally:
            time.sleep(next_iter_start_time - time.time())


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--once", help="Run the bot once and exit", action="store_true")
    parser.add_argument("--date", help="Date to start the program at")
    parser.add_argument(
        "--debug", help="Run the bot in debug mode", action="store_true"
    )

    date = parser.parse_args().date
    date = (
        datetime.datetime.strptime(date, "%Y-%m-%d").date()
        if date
        else datetime.date.today() - datetime.timedelta(days=1)
    )

    debug = parser.parse_args().debug
    if parser.parse_args().once:
        write_tweet(yesterday=date, debug=debug)
    else:
        loop(yesterday=date, debug=debug)
