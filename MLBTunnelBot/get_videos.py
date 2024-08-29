from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import base64
import cv2
import numpy as np

from retrying import retry
import logging
from typing import Optional
from cv2.typing import MatLike
from tqdm import tqdm
import os


JS_PLAY_VIDEO_SCRIPT = """
    var video = arguments[0];
    video.play();
"""

JS_VIDEO_LEN_SCRIPT = """
    return arguments[0].duration;
"""

JS_VIDEO_DOWNLOAD_SCRIPT = """
    var canvas = document.createElement('canvas');
    var video = arguments[0];
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    return canvas.toDataURL('image/png').split(',')[1];
"""


VIDEO_CAPTURE_INTERVAL = 0.01

OUTPUT_VIDEO_PATH = os.path.join(os.path.dirname(__file__), "assets", "videos")


def _init_chrome_options() -> Options:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")

    chrome_options.add_experimental_option(
        "prefs",
        {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.popups": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.media_stream": 2,
        },
    )
    return chrome_options


def _decode_frame(frame: str) -> MatLike:
    """decodes the base64 frame into a cv2 image"""
    nparr = np.frombuffer(base64.b64decode(frame), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


@retry(wait_fixed=3000, stop_max_attempt_number=5)
def get_film_room_video(
    url: str, output_prefix: str, test: bool = False
) -> Optional[list[MatLike]]:
    """retrieves the video frames from the given url"""
    if not os.path.exists(OUTPUT_VIDEO_PATH):
        os.makedirs(OUTPUT_VIDEO_PATH)

    fps = 1 / VIDEO_CAPTURE_INTERVAL
    video_writer = (
        cv2.VideoWriter(
            os.path.join(OUTPUT_VIDEO_PATH, f"{output_prefix}_video.mp4"),
            fourcc=cv2.VideoWriter_fourcc(*"mp4v"),  # type: ignore
            fps=fps,
            frameSize=(1080, 720),
        )
        if not test
        else None
    )

    driver = webdriver.Chrome(service=Service(), options=_init_chrome_options())
    try:
        driver.get(url)
        # grab the video element once it becomes present
        wait = WebDriverWait(driver, 20)
        video_element = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        if not video_element:
            logging.error("Video element not found")
            return None

        # play video and get duration
        driver.execute_script(JS_PLAY_VIDEO_SCRIPT, video_element)
        duration = driver.execute_script(JS_VIDEO_LEN_SCRIPT, video_element)

        video_frames: list[MatLike] = []
        total_frames = int(duration * (fps))
        for i in tqdm(range(total_frames)):
            current_time = i * VIDEO_CAPTURE_INTERVAL
            driver.execute_script(
                f"arguments[0].currentTime = {current_time};", video_element
            )

            time.sleep(VIDEO_CAPTURE_INTERVAL)

            frame = driver.execute_script(JS_VIDEO_DOWNLOAD_SCRIPT, video_element)
            decoded_frame = _decode_frame(frame)
            if not test and video_writer is not None:
                video_writer.write(decoded_frame)
            video_frames.append(decoded_frame)
        return video_frames
    finally:
        driver.quit()
        if video_writer is not None:
            video_writer.release()


if __name__ == "__main__":
    _ = get_film_room_video(
        "https://www.mlb.com/video/tayler-scott-ball-to-cavan-biggio-su0qrj?q=Season%20%3D%20%5B2024%5D%20AND%20Date%20%3D%20%5B%222024-07-27%22%5D%20AND%20PitcherId%20%3D%20%5B605463%5D%20AND%20TopBottom%20%3D%20%5B%22TOP%22%5D%20AND%20Outs%20%3D%20%5B1%5D%20AND%20Balls%20%3D%20%5B1%5D%20AND%20Strikes%20%3D%20%5B2%5D%20AND%20Inning%20%3D%20%5B8%5D%20AND%20PlayerId%20%3D%20%5B624415%5D%20AND%20PitchType%20%3D%20%5B%22FF%22%5D%20Order%20By%20Timestamp%20DESC&cp=MIXED&p=0",
        output_prefix="test",
    )
