import pytest
from songbirdcore import web


@pytest.fixture()
def get_youtube_session():
    return web.SimpleSession("youtube", root_url="https://www.youtube.com")


def test_enter_search_form(get_youtube_session: str):
    """test entering youtube's main search from"""
    session = get_youtube_session
    response = session.enter_search_form(
        search_url="https://www.youtube.com/results",
        payload={"search_query": "billy joel"},
    )
    assert response is not None and response.status_code == 200
