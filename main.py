#
# MLB Tunnel Bot
# Author: Jensen Holm
# April / May 2024
#

import MLBTunnelBot
import datetime
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main() -> None:
    next_iter_start_time = time.time() + (24 * 60 * 60)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    try:
        _ = MLBTunnelBot.write(yesterday=yesterday)
        logging.info(f"Successful write for {yesterday}")

    except MLBTunnelBot.EmptyStatcastDFException as e:
        logging.error(f"Skipping {yesterday} due to empty statcast data: {e}")

    except AssertionError as e:
        logging.error(f"Skipping {yesterday} due to assertion error: {e}.")

    except Exception as e:
        logging.error(f"Unexpected issue for {yesterday}'s write: {e}.")

    finally:
        time.sleep(next_iter_start_time - time.time())


if __name__ == "__main__":

    def _seconds_until_noon_tomorrow() -> float:
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        noon_tmrw = datetime.datetime(
            tomorrow.year,
            tomorrow.month,
            tomorrow.day,
            12,
            0,
        )
        return (noon_tmrw - now).total_seconds()

    wait_time = _seconds_until_noon_tomorrow()
    launch_time = datetime.datetime.now() + datetime.timedelta(seconds=wait_time)
    logging.info(f"sleeping until launch at {launch_time}")
    time.sleep(wait_time)

    while True:
        main()
