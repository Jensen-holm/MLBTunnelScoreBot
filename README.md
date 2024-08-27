# MLB-Tunnel-Bot

The MLB-Tunnel-Bot is a X bot that each day during the MLB season ...

1. Collects statcast pitching data from the day prior
2. Computes pitch tunneling score (statistic that I made)
3. Tweets a sloo of information about that pitch (including links to video, strike zone plot, and the score itself)
4. Does it again the next day

You can find the MLB-Tunnel-Bot on X at [this link](https://twitter.com/MLBTunnelBot)

## Flags

- `--once`: run the bot once and then exit the program. If not set, the bot will run indefinitely
- `--debug`: run the bot in debug mode (no tweets, print to console & exit program)
- `--date`: specify the date to run the bot for (default is yesterday if this is not set)

### Build Locally

**Makefile & Docker**
  1. `make build`
  2. `make run`

**Python virtual environment**
  (requires [virtualenv package](https://pypi.org/project/virtualenv/))
  1. `virtualenv venv`
  2. `source venv/bin/activate`
  3. `pip3 install -r requirements.txt`
  4. `python3 main.py`
