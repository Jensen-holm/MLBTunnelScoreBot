import os


ASSET_DIR = os.path.join("MLBTunnelBot", "assets")
TUNNEL_PLOT_DIR = os.path.join(ASSET_DIR, "tunnel_plot.png")
PROFILE_PIC_DIR = os.path.join(ASSET_DIR, "profile_pic.jpg")
DEFAULT_PROFILE_PIC_DIR = os.path.join(ASSET_DIR, "default_profile_pic.png")

BUILD_TWEET_ARGS: list[str] = [
    "yesterday",
    "pitcher_name",
    "pitch_type",
    "home_team",
    "away_team",
    "film_room_link1",
    "film_room_link2",
    "tunnel_score",
]

KEEPER_COLS: list[str] = [
    "pitcher",
    "batter",
    "home_team",
    "away_team",
    "inning",
    "prev_inning",
    "balls",
    "prev_balls",
    "strikes",
    "prev_strikes",
    "outs_when_up",
    "prev_outs_when_up",
    "des",
    "prev_des",
    "pitch_type",
    "prev_pitch_type",
    "pitch_name",
    "prev_pitch_name",
    "game_date",
    "tunnel_distance",
    "actual_distance",
    "p_throws",
    "stand",
    "inning_topbot",
    "plate_x",
    "plate_z",
    "plate_z_no_movement",
    "plate_x_no_movement",
    "prev_plate_x",
    "prev_plate_z",
    "prev_plate_z_no_movement",
    "prev_plate_x_no_movement",
    "tunnel_score",
    "at_bat_number",
    "pitch_number",
    "prev_pitch_number",
    "release_pos_x",
    "release_pos_z",
    "prev_release_pos_x",
    "prev_release_pos_z",
]

# 2024 mlb team official hashtags
# https://lwosports.com/the-offical-mlb-hashtags-for-the-2024-season/
HASHTAG_MAP: dict[str, str] = {
    "ARI": "DBacks",
    "AZ": "DBacks",
    "ATL": "BravesCountry",
    "BAL": "Birdland",
    "BOS": "DirtyWater",
    "CHC": "YouHaveToSeeIt",
    "CWS": "WhiteSox",
    "CIN": "ATOBTTR",
    "CLE": "ForTheLand",
    "COL": "Rockies",
    "DET": "RepDetroit",
    "MIA": "HomeOfBeisbol",
    "KC": "WelcomeToTheCity",
    "OAK": "Athletics",
    "STL": "ForTheLou",
    "HOU": "Relentless",
    "NYM": "LGM",
    "NYY": "RepBX",
    "SF": "SFGiants",
    "PHI": "RingTheBell",
    "PIT": "LetsGoBucs",
    "MIL": "ThisIsMyCrew",
    "MIN": "MNTwins",
    "LAA": "RepTheHalo",
    "LAD": "LetsGoDodgers",
    "SD": "LetsGoPadres",
    "TB": "RaysUp",
    "WSH": "NATITUDE",
    "SEA": "TridentsUp",
    "TEX": "StraightUpTX",
    "TOR": "TOTHECORE",
}

