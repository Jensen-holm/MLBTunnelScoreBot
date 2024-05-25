#
# Author: Jensen Holm
# Date: 5/23/2024
#

import matplotlib.image as image
import polars as pl
import numpy as np

from typing import Any, Optional
import datetime
import requests
import logging

from .plot_tunnel import plot_strike_zone
from .x_api_info import api, client
from .update import yesterdays_top_tunnel
from .consts import *


def _get_player_headshot(player_mlbam_id: str | float) -> np.ndarray:
    link = f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_mlbam_id}/headshot/67/current"

    r = requests.get(link)
    if r.status_code == 200:
        with open(PROFILE_PIC_DIR, "wb") as f:
            f.write(r.content)
    else:
        logging.warning(
            f"Failed to update profile picture image from {link}. \nPlayer id: {player_mlbam_id}\nUsing Default."
        )

    # no longer updating profile picture. We moved towards putting the
    # player headshot inside of the plot of the tunneled pitch. This function
    # used to be called _update_profile_picture()

    # api.update_profile_image(
    # filename=DEFAULT_PROFILE_PIC_DIR if bad_response else PROFILE_PIC_DIR,
    # )

    headshot_img = image.imread(PROFILE_PIC_DIR)
    return headshot_img


def _build_tweet_text(**kwargs) -> str:
    kwargs = kwargs.get("kwargs", None)
    assert kwargs is not None, "No kwargs passed to _build_tweet_text"
    assert isinstance(kwargs, dict), "kwargs is not a dictionary in _build_tweet_text"

    for arg in BUILD_TWEET_ARGS:
        assert arg in kwargs.keys(), f"{arg} not in build tweet kwargs."
        assert kwargs.get(arg) is not None, f"{arg} is in kwargs, but is None."

    title = f"TOP PITCH BY TUNNEL SCORE {kwargs['yesterday']}"
    t_score = (
        f"{kwargs['pitcher_name']} {kwargs['pitch_type']}: {kwargs['tunnel_score']:.3f}🔥"
    )

    home_hashtag = HASHTAG_MAP.get(kwargs["home_team"], None)
    away_hashtag = HASHTAG_MAP.get(kwargs["away_team"], None)

    assert home_hashtag is not None, f"home hashtag is None for {kwargs['home_team']}"
    assert away_hashtag is not None, f"away hashtag is None for {kwargs['away_team']}"

    team_hashtags = f"#{away_hashtag} @ #{home_hashtag}"

    def _get_ab_result() -> str:
        df = kwargs.get("tunnel_df", None)
        balls = df.select("balls").item()
        strikes = df.select("strikes").item()
        pitch_result = df.select("description").item()
        return "\n".join([
            f"Count: {balls} - {strikes}",
            f"Pitch Result: {pitch_result}",
        ])

    ab_result = _get_ab_result()
    film_room_links = f"MLB Film Room Links:\nprevious pitch: {kwargs['film_room_link1']}\ntunneled pitch: {kwargs['film_room_link2']}"
    other_hashtags = (
        f"#MLBTunnelBot #MLB #Baseball #{''.join(kwargs['pitcher_name'].split())}"
    )
    return "\n\n".join(
        [
            title,
            t_score,
            ab_result,
            team_hashtags,
            film_room_links,
            other_hashtags,
        ]
    )


def _plot_pitches(
    tunneled_pitch: pl.DataFrame, yesterday: datetime.date, player_headshot: np.ndarray
):
    # input should be a polars dataframe with just one pitch
    # and it s previous one

    p1 = tunneled_pitch.select(
        "game_date",
        "at_bat_number",
        "pitch_number",
        "pitch_type",
        "pitch_name",
        "plate_x",
        "plate_z",
        "plate_x_no_movement",
        "plate_z_no_movement",
        "release_pos_x",
        "release_pos_z",
    )

    pitch2 = tunneled_pitch.select(
        "game_date",
        "at_bat_number",
        "prev_pitch_number",
        "prev_pitch_type",
        "prev_pitch_name",
        "prev_plate_x",
        "prev_plate_z",
        "prev_plate_x_no_movement",
        "prev_plate_z_no_movement",
        "prev_release_pos_x",
        "prev_release_pos_z",
    )

    p2 = pitch2.rename(
        {
            col: "_".join(col.split("_")[1:]) if col.startswith("prev") else col
            for col in pitch2.columns
        }
    )

    tunnel_score = tunneled_pitch.select("tunnel_score").item()
    pitcher = tunneled_pitch.select("name").item()

    # saves the plot to assets folder
    _ = plot_strike_zone(
        player_headshot_img=player_headshot,
        data=pitch2.join(
            other=pl.concat([p1, p2]), on=["game_date", "at_bat_number"]
        ).to_pandas(),
        title=f"Best Pitch {yesterday} by Tunnel Score\n{pitcher} {tunnel_score:.2f}",
        colorby="pitch_name",
        annotation="pitch_type",
    )


def write(yesterday: datetime.date, _debug=False) -> None:
    pitch_info: dict[str, Any] = yesterdays_top_tunnel(
        yesterday=yesterday,
    )

    pitcher_id: int = pitch_info.get("pitcher_id", None)
    assert pitcher_id is not None, f"pitcher_id is None."
    assert isinstance(pitcher_id, int), f"pitcher_id is not an integer."

    tunnel_df: Optional[pl.DataFrame] = pitch_info.get("tunnel_df", None)
    assert tunnel_df is not None

    headshot_img = _get_player_headshot(player_mlbam_id=pitcher_id)
    _ = _plot_pitches(
        tunneled_pitch=tunnel_df,
        yesterday=yesterday,
        player_headshot=headshot_img,
    )

    tunnel_plot = api.media_upload(filename=TUNNEL_PLOT_DIR)
    assert tunnel_plot is not None, f"tunnel_plot is None."

    if _debug:
        return

    # TODO: handle twitter api exceptions
    tweet_text = _build_tweet_text(kwargs=pitch_info)
    client.create_tweet(
        text=tweet_text,
        media_ids=[tunnel_plot.media_id],
    )
