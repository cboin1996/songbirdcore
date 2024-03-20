import pytest
from songbirdcore import youtube
import uuid
import os

@pytest.mark.parametrize(
    "video_url",
    [
        "https://www.youtube.com/watch?v=Ixrje2rXLMA",
        "https://www.youtube.com/watch?v=Ixrje2rXLMA"
    ]
)
@pytest.mark.parametrize(
    "fmt",
    [
        "m4a",
        "mp3"
    ]
)
def test_run_download(video_url: str, fmt: str):
    res = youtube.run_download(
        url=video_url,
        file_path_no_format=os.path.join(os.sep, "tmp", str(uuid.uuid4())),
        file_format=fmt
    )
    assert res is not None