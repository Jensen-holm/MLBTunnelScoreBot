from typing import Optional
import requests
import logging

from .x_api_info import api, client
from .update import yesterdays_top_tunnel, YESTERDAY
from .data import (
    hashtag_map,
    TUNNEL_PLOT_DIR,
    PROFILE_PIC_DIR,
    DEFAULT_PROFILE_PIC_DIR,
)


def _update_profile_picture(player_mlbam_id: str | float) -> None:
    link = f"https://img.mlbstatic.com/mlb-photos/image/upload/d_people:generic:headshot:67:current.png/w_426,q_auto:best/v1/people/{player_mlbam_id}/headshot/67/current"

    r = requests.get(link)
    bad_response = False
    if r.status_code == 200:
        with open(PROFILE_PIC_DIR, "wb") as f:
            f.write(r.content)
    else:
        logging.warning(
            f"Failed to update profile picture image from {link}. \nPlayer id: {player_mlbam_id}\nUsing Default."
        )
        bad_response = True

    api.update_profile_image(
        filename=DEFAULT_PROFILE_PIC_DIR if bad_response else PROFILE_PIC_DIR,
    )


def _build_tweet_text(**kwargs) -> str:
    kwargs = kwargs.get("kwargs", None)
    assert kwargs is not None, "No kwargs passed to _build_tweet_text"
    assert isinstance(kwargs, dict), "kwargs is not a dictionary in _build_tweet_text"

    pitcher_name = kwargs.get("pitcher_name")
    pitch_type = kwargs.get("pitch_type")
    home_team = kwargs.get("home_team")
    away_team = kwargs.get("away_team")
    pitch1_link = kwargs.get("film_room_link1")
    pitch2_link = kwargs.get("film_room_link2")
    tunnel_score = kwargs.get("tunnel_score")

    title = f"TOP PITCH BY TUNNEL SCORE {YESTERDAY}"
    t_score = f"{pitcher_name} {pitch_type}: {tunnel_score:.3f}"
    team_hashtags = (
        f"#{hashtag_map.get(home_team, home_team)} vs. "
        f"#{hashtag_map.get(away_team, away_team)}"
    )
    link_text = f"MLB Film Room Links:\nprevious pitch: {pitch1_link}\ntunneled pitch: {pitch2_link}"
    other_hashtags = f"#MLBTunnelBot #MLB #Baseball #{''.join(pitcher_name.split())}"
    return "\n\n".join(
        [
            title,
            t_score,
            link_text,
            team_hashtags,
            other_hashtags,
        ]
    )


def write() -> bool:
    pitch_info: Optional[dict[str, str | float]] = yesterdays_top_tunnel()

    if pitch_info is None:
        logging.warning(f"There must not have been any games on {YESTERDAY}")
        return False

    tunnel_plot = api.media_upload(filename=TUNNEL_PLOT_DIR)
    pitcher_id = pitch_info.get("pitcher_id", None)

    assert tunnel_plot is not None
    assert pitcher_id is not None
    _update_profile_picture(player_mlbam_id=pitcher_id)
    client.create_tweet(
        text=_build_tweet_text(kwargs=pitch_info),
        media_ids=[tunnel_plot.media_id],
    )
    return True

