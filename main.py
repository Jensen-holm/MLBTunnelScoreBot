#
# MLB Tunnel Bot
# Author: Jensen Holm
#

import MLBTunnelBot
import datetime
import logging

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


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "--debug",
        help="Date to start the program at",
        action="store_true",
    )

    _ = write_tweet(
        yesterday=datetime.date.today() - datetime.timedelta(days=1),
        debug=parser.parse_args().debug,
    )
