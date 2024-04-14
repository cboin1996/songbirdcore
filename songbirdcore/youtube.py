import logging
from typing import Optional
from typing import Tuple, List
import requests_html
from bs4 import BeautifulSoup
import os, sys

from .models import itunes_api
from . import web
from . import common

logger = logging.getLogger(__name__)
import yt_dlp as youtube_dl
from yt_dlp.utils import DownloadError, UnavailableVideoError, ExtractorError


def get_video_links(
    youtube_home_url: str,
    youtube_search_url: str,
    youtube_query_payload: dict,
    render_timeout: int,
    render_wait: float,
    retry_count: Optional[int] = 3,
    render_sleep: Optional[int] = 1,
) -> Tuple[List[str], List[requests_html.Element]]:
    """
    Args:
        render_timeout (int): amount of time before abandoning a render
        render_wait (float): the amount of time before attempting a render
        retry_count (int): the number of retries for a render
        render_sleep (Optional[int]): the amount of time to wait after rendering
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",  # ubuntu chrome headers
        "Referrer": youtube_home_url,
    }
    session = web.SimpleSession("youtube", root_url=youtube_home_url, headers=headers)
    tries = 0
    # Only need to log info about these requests on first try to simplify UI experience
    log_attempts = True
    while tries < retry_count:
        # First, enter the search form on the youtube home page
        response = session.enter_search_form(
            search_url=youtube_search_url,
            payload=youtube_query_payload,
            render_timeout=render_timeout,
            render_wait=render_wait,
            render_sleep=render_sleep,
            log_calls=log_attempts,
        )
        if response == None:
            logger.error(
                f"Error occurred performing a search for {youtube_query_payload} against url {youtube_search_url}. Please try again."
            )
            tries += 1
            log_attempts = False
            continue
        # Get the list of hrefs to each video on the home page
        links = response.html.find("#video-title")
        if len(links) == 0:
            logger.warn(f"{tries+1}:{retry_count}.")
            tries += 1
            log_attempts = False
        else:
            break
    session.close()
    if tries >= retry_count:
        logger.error(
            f"Failed to get links from {youtube_home_url} after {retry_count} tries."
        )
        return None

    link_list = []
    # create a user friendly list, containing videos with title and href refs.
    for idx, link in enumerate(links):
        if "title" in link.attrs and "href" in link.attrs:
            link_list.append(
                f"{link.attrs['title']} - {youtube_home_url+link.attrs['href']}"
            )
        # the actual raw list should match list size so we can properly select the link after.
        else:
            links.pop(idx)

    return link_list, links


class YtDlLogger(object):
    """
    Used for setting up youtube_dl logging
    """

    def info(self, msg):
        logger.info(msg)

    def debug(self, msg):
        logger.debug(msg)

    def warning(self, msg):
        logger.warning(msg)

    def error(self, msg):
        logger.error(msg)


def my_hook(d):
    """
    Hook for youtube_dl
    Args:
        d: download object from youtube_dl
    """
    if d["status"] == "finished":
        sys.stdout.write("\n")
        logger.info("Done downloading, now converting ...")

    if d["status"] == "downloading":
        p = d["_percent_str"]
        p = p.replace("%", "")
        song_name = d["filename"].split(os.sep)[-1]
        sys.stdout.write(
            f"\rDownloading to file: {song_name}, {d['_percent_str']}, {d['_eta_str']}"
        )
        sys.stdout.flush()
    if d["status"] == "error":
        logger.error("Error occured during download.")
        success_downloading = False


def run_download(url: str, file_path_no_format: str, file_format: str) -> str:
    """Run a download from youtube

    Args:
        url (str): the url to download
        file_path_no_format (str): the file path excluding file format
        file_format (str): the file format
    Returns:
        str: the filepath.
    """
    local_file_path = f"{file_path_no_format}.{file_format}"
    ydl_opts = {
        "format": "bestaudio/best",
        "cachedir": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": file_format,
                "preferredquality": "192",
            }
        ],
        "nocheckcertificate": True,
        "logger": YtDlLogger(),
        "progress_hooks": [my_hook],
        "outtmpl": file_path_no_format + ".%(ext)s",
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
        logger.info(f"Downloading successful. File stored locally: {local_file_path}")
        return local_file_path
    except Exception as e:
        logger.exception(f"Failed to complete the download of song at url: {url}.")
        return None
