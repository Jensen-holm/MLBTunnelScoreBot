import MLBTunnelBot.x as MLBTunnelBot
from MLBTunnelBot.update import YESTERDAY
import logging
import time


def mainloop() -> None:
    while True:
        success: bool = MLBTunnelBot.write()
        if not success:
            logging.warning(
                # the specific reason for why it
                # failed will have been logged before this
                f"Skipping {YESTERDAY} due to unsuccessful write."
            )

        time.sleep(24 * 60 * 60)


if __name__ == "__main__":
    mainloop()
