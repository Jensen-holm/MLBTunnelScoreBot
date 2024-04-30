import polars as pl
import numpy as np
import pybaseball
import datetime


def _get_yesterdays_pitches() -> pl.DataFrame:
    yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
    return pl.from_pandas(pybaseball.statcast(start_dt=yesterday, end_dt=yesterday))


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

def _compute_tunnel_plus(statcast_pitches_df: pl.DataFrame) -> pl.DataFrame:
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
        )
    )


def main() -> None:
    yesterdays_df: pl.DataFrame = _get_yesterdays_pitches()
    tied_df: pl.DataFrame = _tie_pitches_to_previous(yesterdays_df)
    tunnel_df: pl.DataFrame = _compute_tunnel_plus(tied_df)

    # drop missing values from tunnel_df
    tunnel_df.drop_nulls(subset=[
        "",
    ])


if __name__ == "__main__":
    main()
