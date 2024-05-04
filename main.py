# MLB Tunnel Bot
# Author: Jensen Holm
# April / May 2024

# disable tqdm progress bar used in pybaseball
import os

os.environ["TQDM_DISABLE"] = "1"

import MLBTunnelBot
import datetime
import logging
import time

# configure logger
logging.basicConfig(level=logging.INFO)


def mainloop() -> None:
    while True:
        next_iter_start_time = time.time() + (24 * 60 * 60)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)

        try:
            _ = MLBTunnelBot.write(yesterday=yesterday)
            logging.info(f"Successful write for {yesterday}")

        except MLBTunnelBot.EmptyStatcastDFException:
            logging.error(f"Skipping {yesterday} due to empty statcast data.")

        except AssertionError as e:
            logging.error(f"Skipping {yesterday} due to assertion error: {e}.")

        except Exception as e:
            logging.error(f"Unexpected issue for {yesterday}'s write: {e}.")

        finally:
            sleep_time = next_iter_start_time - time.time()
            time.sleep(sleep_time)


if __name__ == "__main__":
    mainloop()
