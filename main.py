import MLBTunnelBot
import datetime
import logging
import time


logging.basicConfig(level=logging.INFO)


def mainloop() -> None:
    while True:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        start_time = time.time()

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
            end_time = time.time()
            sleep_time = (24 * 60 * 60) - (end_time - start_time)
            logging.info(
                f"Sleeping until {datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)}"
            )
            time.sleep(sleep_time)


if __name__ == "__main__":
    mainloop()
