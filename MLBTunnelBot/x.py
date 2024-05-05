import datetime
from typing import Any
import requests
import logging

from .x_api_info import api, client
from .update import yesterdays_top_tunnel
from .consts import *


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

    for arg in BUILD_TWEET_ARGS:
        assert arg in kwargs.keys(), f"{arg} not in build tweet kwargs."
        assert kwargs.get(arg) is not None, f"{arg} is in kwargs, but is None."

    title = f"TOP PITCH BY TUNNEL SCORE {kwargs['yesterday']}"
    t_score = (
        f"{kwargs['pitcher_name']} {kwargs['pitch_type']}: {kwargs['tunnel_score']:.3f}"
    )

    home_hashtag = HASHTAG_MAP.get(kwargs["home_team"], None)
    away_hashtag = HASHTAG_MAP.get(kwargs["away_team"], None)

    assert home_hashtag is not None, f"home hashtag is None for {kwargs['home_team']}"
    assert away_hashtag is not None, f"away hashtag is None for {kwargs['away_team']}"

    team_hashtags = f"#{away_hashtag} @ #{home_hashtag}"

    link_text = f"MLB Film Room Links:\nprevious pitch: {kwargs['film_room_link1']}\ntunneled pitch: {kwargs['film_room_link2']}"
    other_hashtags = (
        f"#MLBTunnelBot #MLB #Baseball #{''.join(kwargs['pitcher_name'].split())}"
    )
    return "\n\n".join(
        [
            title,
            t_score,
            link_text,
            team_hashtags,
            other_hashtags,
        ]
    )


def write(yesterday: datetime.date, _debug=False) -> None:
    pitch_info: dict[str, Any] = yesterdays_top_tunnel(
        yesterday=yesterday,
    )

    tunnel_plot = api.media_upload(filename=TUNNEL_PLOT_DIR)
    pitcher_id = pitch_info.get("pitcher_id", None)

    assert pitcher_id is not None, f"pitcher_id is None."
    assert isinstance(pitcher_id, int), f"pitcher_id is not an integer."
    assert tunnel_plot is not None, f"tunnel_plot is None."

    if _debug:
        return

    # TODO: handle twitter api exceptions
    _update_profile_picture(player_mlbam_id=pitcher_id)

    client.create_tweet(
        text=_build_tweet_text(kwargs=pitch_info),
        media_ids=[tunnel_plot.media_id],
    )
