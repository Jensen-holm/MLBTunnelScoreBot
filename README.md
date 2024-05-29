# MLB-Tunnel-Bot

The MLB-Tunnel-Bot is a X bot that each day during the MLB season ...

1. Collects statcast pitching data from the day prior
2. Computes pitch tunneling score (statistic that I made)
3. Tweets a sloo of information about that pitch (including links to video, strike zone plot, and the score itself)
4. Does it again the next day

You can find the MLB-Tunnel-Bot on X at [this link](https://twitter.com/MLBTunnelBot)

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

