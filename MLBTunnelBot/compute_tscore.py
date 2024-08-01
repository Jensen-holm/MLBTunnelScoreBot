#
# Author: Jensen Holm
# Date: 05/28/2024
#

import warnings
import os

# ignore pybaseball tqdm progress bar and also ignore
# the pandas FutureWarning that pybaseball causes
os.environ["TQDM_DISABLE"] = "1"
warnings.simplefilter(action="ignore", category=FutureWarning)


import math
import polars as pl
import pandas as pd
import numpy as np
import datetime
import pybaseball
from typing import Any

from .exceptions import EmptyStatcastDFException
from .consts import KEEPER_COLS

MLB_FILMROOM_URL = "https://www.mlb.com/video/?q=Season+%3D+%5B{year}%5D+AND+Date+%3D+%5B%22{yesterday}%22%5D+AND+PitcherId+%3D+%5B{pitcher_id}%5D+AND+TopBottom+%3D+%5B%22{top_bot}%22%5D+AND+Outs+%3D+%5B{outs}%5D+AND+Balls+%3D+%5B{balls}%5D+AND+Strikes+%3D+%5B{strikes}%5D+AND+Inning+%3D+%5B{inning}%5D+AND+PlayerId+%3D+%5B{hitter_id}%5D+AND+PitchType+%3D+%5B%22{pitch_type}%22%5D+Order+By+Timestamp+DESC"


def _get_yesterdays_pitches(yesterdays_date: datetime.date) -> pl.DataFrame:
    """
    Retrieves yesterday's statcast pitch data using pybaseball's statcast function.

    @params
        yesterdays_date: datetime.date object for yesterdays date

    @returns
        polars dataframe containing yesterdays statcast pitch data.
    """
    yesterday_df: pl.DataFrame = pl.from_pandas(
        pybaseball.statcast(
            start_dt=f"{yesterdays_date}",
            end_dt=f"{yesterdays_date}",
            verbose=False,
        )
    )

    if yesterday_df.is_empty():
        raise EmptyStatcastDFException(
            "yesterday_df is empty in MLBTunnelBot.update.py"
        )

    return yesterday_df


def _tie_pitches_to_previous(pitches_df: pl.DataFrame) -> pl.DataFrame:
    """
    Takes in a polars dataframe of statcast pitch data and sorts it so that
    we have the pitches in descending order from most recently thrown to oldest
    thrown. Then, we add columns for the previous pitch in the at bat.

    @params
        pitches_df: polars dataframe of statcast pitch data.

    @returns
        A new polars dataframe sorted by game date, pitcher id, at bat number
        and pitch number that has added columns containing data from the previous
        pitch thrown in an at bat.
    """
    sorted_pitches = pitches_df.sort(
        ["game_date", "pitcher", "at_bat_number", "pitch_number"],
        descending=True,
    )

    for col_name in sorted_pitches.columns:
        sorted_pitches = sorted_pitches.with_columns(
            pl.col(col_name)
            .shift(-1)
            .over(["pitcher", "at_bat_number"])
            .alias(f"prev_{col_name}")
        )
    return sorted_pitches


def _get_player_names(pitches_df: pl.DataFrame) -> pl.DataFrame:
    """
    Takes a polars dataframe of statcast pitch data without player names
    and adds the player names to it in new columns "pitcher_name" and "hitter_name"
    using pybaseball functions for reverse player lookup and the mlbam id's
    for the player.

    @params
        pitches_df: polars dataframe of statcast pitch data without
                    the player names.

    @returns
        the same polars dataframe but with player names added to it.
    """
    pitchers = pybaseball.playerid_reverse_lookup(
        [pitcher["pitcher"] for pitcher in pitches_df.iter_rows(named=True)],
        key_type="mlbam",
    )

    hitters = pybaseball.playerid_reverse_lookup(
        [batter["batter"] for batter in pitches_df.iter_rows(named=True)],
        key_type="mlbam",
    )
    pitchers["pitcher_name"] = (
        pitchers["name_first"] + " " + pitchers["name_last"]
    ).str.title()

    pitchers["hitter_name"] = (
        hitters["name_first"] + " " + hitters["name_last"]
    ).str.title()

    pitchers["hitter_id"] = hitters["key_mlbam"]
    subset = pitchers[["key_mlbam", "pitcher_name", "hitter_name", "hitter_id"]]

    assert isinstance(subset, pd.DataFrame), "name subset is not a dataframe."

    return pitches_df.join(
        other=pl.from_pandas(subset),
        left_on="pitcher",
        right_on="key_mlbam",
    )


def _compute_tunnel_score(statcast_pitches_df: pl.DataFrame) -> pl.DataFrame:
    """
    Tunnel Score = (actualdistance / tunneldistance) - releasedistance

    @params
        statcast_pitches_df: polars dataframe of statcast pitch data that
                            has columns describing the previous pitch (see _tie_pitches_to_previous).

    @returns
        the same dataframe but with added columns that are included in the
        calculation of tunnel score, and tunnel score itself. This includes
        "plate_x_no_movement", "plate_z_no_movement", "prev_plate_x_no_movement",
        "prev_plate_z_no_movement", "tunnel_distance", "actual_distance",
        "release_distance" and "tunnel_score".
    """

    def _euclidean_distance(point1: tuple[pl.Expr, ...], point2: tuple[pl.Expr, ...]):
        """
        In this case the euclidean distance describes how far in inches
        two different pitch locations are from each other.

        euclidean distance is calculated by the formula:
            sqrt(((x1 - x2) ** 2 + (y1 - y2) ** 2))
        """
        x1, y1 = point1
        x2, y2 = point2
        return np.sqrt(((x1 - x2) ** 2 + (y1 - y2) ** 2))

    statcast_with_no_move = statcast_pitches_df.with_columns(
        plate_x_no_movement=pl.col("plate_x") - pl.col("pfx_x"),
        plate_z_no_movement=pl.col("plate_z") - pl.col("pfx_z"),
        prev_plate_x_no_movement=pl.col("prev_plate_x") - pl.col("prev_pfx_x"),
        prev_plate_z_no_movement=pl.col("prev_plate_z") - pl.col("prev_pfx_z"),
    )

    statcast_with_distances = statcast_with_no_move.with_columns(
        tunnel_distance=_euclidean_distance(
            point1=(pl.col("plate_x_no_movement"), pl.col("plate_z_no_movement")),
            point2=(
                pl.col("prev_plate_x_no_movement"),
                pl.col("prev_plate_z_no_movement"),
            ),
        ),
        actual_distance=_euclidean_distance(
            point1=(pl.col("plate_x"), pl.col("plate_z")),
            point2=(pl.col("prev_plate_x"), pl.col("prev_plate_z")),
        ),
        release_distance=_euclidean_distance(
            point1=(pl.col("release_pos_x"), pl.col("release_pos_z")),
            point2=(pl.col("prev_release_pos_x"), pl.col("release_pos_z")),
        ),
    )
    return statcast_with_distances.with_columns(
        tunnel_score=(pl.col("actual_distance") / pl.col("tunnel_distance"))
        - pl.col("release_distance"),
    )


def _get_film_room_videos(
    pitch: pl.DataFrame, yesterday: datetime.date
) -> tuple[str, str]:
    """
    Takes in a polars dataframe containing data from only one pitch and yesterdays date
    and returns mlb filmroom search filters for that pitch. Note that sometimes the pitch
    is not actually on MLB filmroom, but sometimes it is.

    @params
        pitch: polars dataframe containing statcast pitch data from just one pitch.
        yesterday: datetime.date object for yesterdays date (date of the pitch).

    @returns
        tuple of MLB Filmroom links.
    """
    assert (
        len(pitch) == 1
    ), "only a polars df with one row can be passed into _get_film_room_video."

    inning = pitch.select("inning").item()
    top_bot = (
        pitch.select("inning_topbot").item().upper()
    )  # needs to be either TOP or BOT
    balls = pitch.select("balls").item()
    strikes = pitch.select("strikes").item()
    pitcher_id = pitch.select("pitcher").item()
    outs = pitch.select("outs_when_up").item()
    pitch_type = pitch.select("pitch_type").item()
    hitter_id = pitch.select("hitter_id").item()

    prev_pitch_type = pitch.select("prev_pitch_type").item()
    prev_outs = pitch.select("prev_outs_when_up").item()  # shouldn't this be the same ?
    prev_strikes = pitch.select("prev_strikes").item()
    prev_balls = pitch.select("prev_balls").item()

    year = yesterday.year

    tunneled_filmroom_link = MLB_FILMROOM_URL.format(
        year=year,
        yesterday=yesterday,
        inning=inning,
        top_bot=top_bot,
        balls=balls,
        strikes=strikes,
        pitcher_id=pitcher_id,
        outs=outs,
        pitch_type=pitch_type,
        hitter_id=hitter_id,
    )
    previous_filmroom_link = MLB_FILMROOM_URL.format(
        year=year,
        yesterday=yesterday,
        inning=inning,
        top_bot=top_bot,
        balls=prev_balls,
        strikes=prev_strikes,
        pitcher_id=pitcher_id,
        outs=prev_outs,
        pitch_type=prev_pitch_type,
        hitter_id=hitter_id,
    )
    return tunneled_filmroom_link, previous_filmroom_link


def yesterdays_top_tunnel(yesterday: datetime.date) -> dict[str, Any]:
    """
    Acts as the main function for this compute_tscore.py module. Takes in
    yesterday's date, then uses the functions above to retrieve yesterdays
    statcast pitch data, cleans it, computes tunnel score, and collects mlb
    filmroom links of the pitch.

    @params
        yesterday: datetime.date object for yesterday's date

    @returns
        dictionary object containing all of the useful information about the pitch
        so that we can tweet about it.
    """
    yesterdays_df: pl.DataFrame = _get_yesterdays_pitches(yesterday)

    tied_df: pl.DataFrame = _tie_pitches_to_previous(yesterdays_df)
    tunnel_df: pl.DataFrame = _compute_tunnel_score(tied_df)

    # drop missing values from tunnel_df
    tunnel_df = tunnel_df.drop_nulls(subset=KEEPER_COLS).select(
        KEEPER_COLS,
    )

    tunnel_df = (
        tunnel_df.drop_nulls(subset=KEEPER_COLS)
        .select(KEEPER_COLS)
        .sort("tunnel_score", descending=True)
        .head(1)
    )

    tunnel_df = _get_player_names(tunnel_df)  # add player names to the dataframe

    # used to plot the pitches here and save the result to assets
    # but now we pass tunnel_df into the dictionary this fn returns
    # and it gets plotted in x.py so that we can add player headshot
    # to the middle of the plot

    tunneled_filmroom_link, prev_filmroom_link = _get_film_room_videos(
        pitch=tunnel_df,
        yesterday=yesterday,
    )

    # take log_2 of tunnel score to get the final value. This is being
    # done in order to avoid infinite tunnel score values when the denominator
    # is really small.
    tunnel_score = math.log(tunnel_df.select("tunnel_score").item(), 2)

    return dict(
        yesterday=yesterday,
        pitcher_name=tunnel_df.select("pitcher_name").item(),
        pitcher_id=tunnel_df.select("pitcher").item(),
        pitch_name=tunnel_df.select("pitch_name").item(),
        home_team=tunnel_df.select("home_team").item(),
        away_team=tunnel_df.select("away_team").item(),
        tunnel_score=tunnel_score,
        hitter_id=tunnel_df.select("hitter_id").item(),
        hitter_name=tunnel_df.select("hitter_name").item(),
        tunneled_filmroom_link=tunneled_filmroom_link,
        prev_filmroom_link=prev_filmroom_link,
        tunnel_df=tunnel_df,
    )
