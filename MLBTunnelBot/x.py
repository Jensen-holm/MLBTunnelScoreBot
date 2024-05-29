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
from .compute_tscore import yesterdays_top_tunnel
from .consts import *

HEADSHOT_BASE_URL = "https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_mlbam_id}/headshot/67/current"


def _get_player_headshot(player_mlbam_id: str | float) -> np.ndarray:
    """
    Scrapes the players headshot with the given mlbam id from the
    HEADSHOT_BASE_URL url. This function both returns the numpy array
    of image data from the players headshot as well as saves the image
    to the assets directory under the name "assets/profile_pic.jpg"

    @params
        player_mlbam_id: string of the players mlbam id.

    @return
        numpy array of the image data from the players headshot.
    """

    url = HEADSHOT_BASE_URL.format(player_mlbam_id=player_mlbam_id)

    r = requests.get(url)
    if r.status_code == 200:
        with open(PROFILE_PIC_DIR, "wb") as f:
            f.write(r.content)
    else:
        logging.warning(
            f"Failed to update profile picture image from {url}. \nPlayer id: {player_mlbam_id}\nUsing Default."
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
    """
    takes in the gathered information from the pitch
    with the higest tunnel score and builds the tweet
    text using this information.

    @params
        kwargs: dictionary of key word arguments which
                must have the specified keys from consts.BUILD_TWEET_ARGS
                or else an assertion error will be raised.

    @returns
        final tweet text in string format.
    """

    kwargs = kwargs.get("kwargs", None)
    assert kwargs is not None, "No kwargs passed to _build_tweet_text"
    assert isinstance(kwargs, dict), "kwargs is not a dictionary in _build_tweet_text"

    for arg in BUILD_TWEET_ARGS:
        assert arg in kwargs.keys(), f"{arg} not in build tweet kwargs."
        assert kwargs.get(arg) is not None, f"{arg} is in kwargs, but is None."

    title = f"TOP PITCH BY TUNNEL SCORE {kwargs['yesterday']}"
    t_score = f"{kwargs['pitcher_name']} {kwargs['pitch_name']}: {kwargs['tunnel_score']:.3f}🔥"
    home_hashtag = HASHTAG_MAP.get(kwargs["home_team"], None)
    away_hashtag = HASHTAG_MAP.get(kwargs["away_team"], None)

    assert home_hashtag is not None, f"home hashtag is None for {kwargs['home_team']}"
    assert away_hashtag is not None, f"away hashtag is None for {kwargs['away_team']}"

    team_hashtags = f"#{away_hashtag} @ #{home_hashtag}"
    film_room_links = f"MLB Film Room Links:\nprevious pitch: {kwargs['prev_filmroom_link']}\ntunneled pitch: {kwargs['tunneled_filmroom_link']}"
    return "\n\n".join(
        [
            title,
            t_score,
            team_hashtags,
            film_room_links,
        ]
    )


def _plot_pitches(
    tunneled_pitch: pl.DataFrame, yesterday: datetime.date, player_headshot: np.ndarray
) -> None:
    """
    Takes the collected information about the best tunneled pitch and makes a matplotlib
    plot using functions from MLBTunnelBot/plot_tunnel.py and saves it to the assets folder
    under the name "assets/tunnel_plot.png".

    @params
        tunneled_pitch: polars dataframe containing statcast pitch data from the best
                        tunneled pitch and data from the previous one.
        yesterday: datetime.date object for yesterday's date (date of the pitch).
        player_headshot: numpy array of data for the players headshot image

    @returns
        None
    """
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
    pitcher = tunneled_pitch.select("pitcher_name").item()

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


def write(yesterday: datetime.date, _debug=False) -> str:
    """
    serves as the main function for this entire program.
    write() will post the tweet to x depending on the value
    of the _debug parameter.

    @params
        yesterday: datetime.date object of yesterday's date.
        _debug: boolean value, if true will not post to x.

    @returns
        the generated tweet text.
    """
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

    tweet_text = _build_tweet_text(kwargs=pitch_info)

    if _debug:
        return tweet_text

    client.create_tweet(
        text=tweet_text,
        media_ids=[tunnel_plot.media_id],
    )

    return tweet_text
