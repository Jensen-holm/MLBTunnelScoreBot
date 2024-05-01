# MLB-Tunnel-Bot

The MLB-Tunnel-Bot is a X bot that each day during the MLB season ...

1. Collects statcast pitching data from the day prior
2. Computes pitch tunneling score (statistic that I made)
3. Tweets a sloo of information about that pitch (including links to video, strike zone plot, and the score itself)
4. Does it again the next day

You can find the MLB-Tunnel-Bot on X at [this link](https://twitter.com/MLBTullelBot)

The profile picture updates each day with the pitcher who threw the best tunneled pitch that day.


## Data Source

Data for this project is hosted in a [hugging face dataset repository](https://huggingface.co/datasets/Jensen-holm/statcast-era-pitches) that contains a parquet file with every MLB pitch from the Statcast era up through the last season (2015-2023 as of now).

## To update Hugging Face repo (without github actions)
 - $ git remote add space git@hf.co:Jensen-holm/bsbl-tomorrow
 - $ git push --force space main
