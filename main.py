import MLBTunnelBot
import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def write_tweet(date: datetime.date, debug: bool) -> None:
    try:
        tweet = MLBTunnelBot.write(yesterday=date, debug=debug)
        logging.info(f"Successful write for {yesterday}\n{tweet}")
    except Exception as e:
        logging.error(f"Error for {yesterday} due to exception: {e.__class__} -> {e}")


def yesterday() -> datetime.date:
    return datetime.date.today() - datetime.timedelta(days=1)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "--debug",
        help="Date to start the program at",
        action="store_true",
    )
    parser.add_argument(
        "--date",
        help="Date to start the program at, default is yesterday (ISO 8601 format: YYYY-MM-DD)",
        type=datetime.date.fromisoformat,
    )

    date = parser.parse_args().date
    debug = parser.parse_args().debug
    _ = write_tweet(
        date=yesterday() if date is None else date,
        debug=parser.parse_args().debug,
    )
