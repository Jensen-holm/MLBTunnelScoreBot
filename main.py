import MLBTunnelBot.x as MLBTunnelBot
import time


def mainloop() -> None:
    while True:
        _ = MLBTunnelBot.write()
        time.sleep(24 * 60 * 60)


if __name__ == "__main__":
    mainloop()
