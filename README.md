# MLB-Tunnel-Bot

<p align="center">
  The MLB-Tunnel-Bot is a X bot that finds the best pitch tunneling scores from the day before and tweets about them. <br>
  You can find the MLB-Tunnel-Bot on X at [this link](https://twitter.com/MLBTunnelBot) <br>
</p>

<div align="center">
  <img src="PLACEHOLDER_FOR_LATEST_IMAGE" alt="Latest, Highest Tunnel Score Plot" width="500" height="500">
</div>

1. Collects statcast pitching data from the day prior
2. Computes pitch tunneling score (statistic that I made)
3. Tweets a sloo of information about that pitch (including links to video, strike zone plot, and the score itself)
4. Does it again the next day

You can find the MLB-Tunnel-Bot on X at [this link](https://twitter.com/MLBTunnelBot)

## Flags

- `--debug`: run the bot in debug mode (does post tweet, prints it to console & exit program)

## Build Locally

**Makefile & Docker**
  1. `make build`
  2. `make run`

**Python virtual environment**
  (requires [virtualenv package](https://pypi.org/project/virtualenv/))
  1. `virtualenv venv`
  2. `source venv/bin/activate`
  3. `pip3 install -r requirements.txt`
  4. `python3 main.py --once --debug`

## Notes

This will only work with valid X api keys.
