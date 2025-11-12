import pytest
from songbirdcore import youtube
import uuid
import os


@pytest.mark.skipif(
    os.getenv("ENV", None) not in ["dev", "test"],
    reason="Test should only be run locally, signified by ENV=dev|test",
)
@pytest.mark.parametrize(
    "video_url",
    [
        "https://www.youtube.com/watch?v=Ixrje2rXLMA",
        "https://www.youtube.com/watch?v=wOwblaKmyVw",
    ],
)
@pytest.mark.parametrize("fmt", ["m4a", "mp3"])
@pytest.mark.parametrize("embed_thumbnail", [True, False])
def test_run_download(video_url: str, fmt: str, embed_thumbnail: bool):
    res = youtube.run_download(
        url=video_url,
        file_path_no_format=os.path.join(os.sep, "tmp", str(uuid.uuid4())),
        file_format=fmt,
        embed_thumbnail=embed_thumbnail,
    )
    assert res is not None


def test_get_video_links():
    youtube_home_url: str = "https://www.youtube.com"
    youtube_search_url: str = "https://www.youtube.com/results"
    youtube_search_payload: dict = {"search_query": "jolene dolly parton"}

    link_list, links = youtube.get_video_links(
        youtube_home_url=youtube_home_url,
        youtube_search_url=youtube_search_url,
        youtube_query_payload=youtube_search_payload,
        render_timeout=20,
        render_wait=0.2,
        retry_count=3,
        render_sleep=1,
    )

    assert len(link_list) > 0 and len(links) > 0
