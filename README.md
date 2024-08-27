# MLB-Tunnel-Bot

The MLB-Tunnel-Bot is a X bot that finds the best pitch tunneling scores from the day before and tweets about them. You can find the MLB-Tunnel-Bot on X at [this link](https://twitter.com/MLBTunnelBot).

## Tunnel Score

Read more about how the tunnel score statistic is calculated [here](https://t.co/R0Haj08fty)

The video on the right is an example of a pitch that has a really good tunnel score, and the video on the left is the pitch before it. You can see that both pitches start out on the same initial trajectory, and end up in very different places in the strike zone. 

The goal of tunnel score is to put a number to this, and reward pitches that 'looked the same' at the start of the pitch as the previous one, and ended up in different places. 

<div align="center">
  <img src="prev.gif" height="240" width="320"/>
  <img src="tunnel.gif" height="240" width="320"/>
</div>

## Example Tweet

<div align="center">
  <img src="example_tweet.png" height="500" width="500" />
</div>

## Notes

The `main.py` program is run as a cron job once every day at 3:50:00 PM UTC, which is 11:50:00 AM EST. This cron job will tweet the highest tunnel score from the day before.

### Flags

- `--debug`: run the bot in debug mode (does post tweet, prints it to console & exit program)

### Build Locally

**Python virtual environment**
  (requires [virtualenv package](https://pypi.org/project/virtualenv/))
  1. `virtualenv venv`
  2. `source venv/bin/activate`
  3. `pip3 install -r requirements.txt`
  4. `python3 main.py --debug`

### Roadmap

- [x] run as a cron job
- [ ] web dashboard
- [ ] scrape videos of the best tunneled pitches, overlay them, and tweet the video
