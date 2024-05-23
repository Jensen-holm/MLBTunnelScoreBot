import warnings
import os

# ignore pybaseball tqdm progress bar and also ignore
# the pandas FutureWarning that pybaseball causes
os.environ["TQDM_DISABLE"] = "1"
warnings.simplefilter(action="ignore", category=FutureWarning)


import polars as pl
import pandas as pd
import numpy as np
import datetime
import pybaseball
from typing import Any

from .exceptions import EmptyStatcastDFException
from .consts import KEEPER_COLS


def _get_yesterdays_pitches(yesterdays_date: datetime.date) -> pl.DataFrame:
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
    sorted_pitches = pitches_df.sort(
        ["game_date", "pitcher", "at_bat_number", "pitch_number"],
        descending=True,
    )

    for col_name in sorted_pitches.columns:
        sorted_pitches = sorted_pitches.with_columns(
            pl.col(col_name).shift(1).over("pitcher").alias(f"prev_{col_name}")
        )
    return sorted_pitches


def _get_player_names(pitches_df: pl.DataFrame) -> pl.DataFrame:
    pitchers = pybaseball.playerid_reverse_lookup(
        [pitcher["pitcher"] for pitcher in pitches_df.iter_rows(named=True)],
        key_type="mlbam",
    )
    pitchers["name"] = (
        pitchers["name_first"] + " " + pitchers["name_last"]
    ).str.title()

    subset = pitchers[["key_mlbam", "name"]]
    assert isinstance(
        subset, pd.DataFrame
    ), "name subset is not a dataframe."  # just to make my editor happy
    return pitches_df.join(
        other=pl.from_pandas(subset),
        left_on="pitcher",
        right_on="key_mlbam",
    )


def _compute_tunnel_score(statcast_pitches_df: pl.DataFrame) -> pl.DataFrame:
    def _euclidean_distance(point1: tuple[pl.Expr, ...], point2: tuple[pl.Expr, ...]):
        x1, y1 = point1
        x2, y2 = point2
        return np.sqrt(((x1 - x2) ** 2 + (y1 - y2) ** 2))

    statcast_with_no_move = statcast_pitches_df.with_columns(
        plate_x_no_movement=pl.col("plate_x") - pl.col("pfx_x"),
        plate_z_no_movement=pl.col("plate_z") - pl.col("pfx_z"),
        prev_plate_x_no_movement=pl.col("prev_plate_x") - pl.col("prev_pfx_x"),
        prev_plate_z_no_movement=pl.col("prev_plate_z") - pl.col("prev_pfx_z"),
    )

    return statcast_with_no_move.with_columns(
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
    ).with_columns(
        tunnel_score=(pl.col("actual_distance") / pl.col("tunnel_distance"))
        - pl.col("release_distance"),
    )


def _get_film_room_video(
    pitch: pl.DataFrame, yesterday: datetime.date
) -> tuple[str, str]:
    inning = pitch.select("inning").item()
    top_bot = pitch.select("inning_topbot").item()  # needs to be either TOP or BOT
    balls = pitch.select("balls").item()
    strikes = pitch.select("strikes").item()
    pitcher_id = pitch.select("pitcher").item()
    outs = pitch.select("outs_when_up").item()

    prev_outs = pitch.select("prev_outs_when_up").item()
    prev_strikes = pitch.select("prev_strikes").item()
    prev_balls = pitch.select("prev_balls").item()

    year = yesterday.year
    return (
        f"https://www.mlb.com/video/?q=Season+%3D+%5B{year}%5D+AND+Date+%3D+%5B%22{yesterday}%22%5D+AND+PitcherId+%3D+%5B{pitcher_id}%5D+AND+TopBottom+%3D+%5B%22{top_bot.upper()}%22%5D+AND+Outs+%3D+%5B{outs}%5D+AND+Balls+%3D+%5B{balls}%5D+AND+Strikes+%3D+%5B{strikes}%5D+AND+Inning+%3D+%5B{inning}%5D+Order+By+Timestamp+DESC",
        f"https://www.mlb.com/video/?q=Season+%3D+%5B{year}%5D+AND+Date+%3D+%5B%22{yesterday}%22%5D+AND+PitcherId+%3D+%5B{pitcher_id}%5D+AND+TopBottom+%3D+%5B%22{top_bot.upper()}%22%5D+AND+Outs+%3D+%5B{prev_outs}%5D+AND+Balls+%3D+%5B{prev_balls}%5D+AND+Strikes+%3D+%5B{prev_strikes}%5D+AND+Inning+%3D+%5B{inning}%5D+Order+By+Timestamp+DESC",
    )


def yesterdays_top_tunnel(yesterday: datetime.date) -> dict[str, Any]:
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

    film_room_link1, film_room_link2 = _get_film_room_video(
        pitch=tunnel_df,
        yesterday=yesterday,
    )
    return dict(
        yesterday=yesterday,
        pitcher_name=tunnel_df.select("name").item(),
        pitcher_id=tunnel_df.select("pitcher").item(),
        pitch_type=tunnel_df.select("pitch_name").item(),
        home_team=tunnel_df.select("home_team").item(),
        away_team=tunnel_df.select("away_team").item(),
        tunnel_score=tunnel_df.select("tunnel_score").item(),
        film_room_link1=film_room_link1,
        film_room_link2=film_room_link2,
        tunnel_df=tunnel_df,
    )
