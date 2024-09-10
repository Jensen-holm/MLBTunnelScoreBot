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
        logging.info(f"Successful write for {date}\n{tweet}")
    except Exception as e:
        logging.error(f"Error for {date} due to exception: {e.__class__} -> {e}")


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
        default=yesterday(),
    )

    _ = write_tweet(**vars(parser.parse_args()))
