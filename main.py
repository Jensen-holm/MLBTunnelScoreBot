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

    tweet = MLBTunnelBot.write(yesterday=yesterday, _debug=True)
    print(tweet)

    # try:
    #     tweet = MLBTunnelBot.write(yesterday=yesterday, _debug=True)
    #     logging.info(f"Successful write for {yesterday}\n{tweet}")

    # except Exception as e:
    #     logging.error(f"Error for {yesterday} due to exception: {e.__class__} -> {e}")

    # finally:
    #     time.sleep(next_iter_start_time - time.time())


if __name__ == "__main__":
    main()
