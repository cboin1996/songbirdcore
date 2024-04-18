import pytest

from typing import List, Union
import shutil
import os, sys

from songbirdcore import itunes
from songbirdcore.models import modes, itunes_api
from test_common import create_test_folder

RESOURCES_FOLDER = "resources"


@pytest.fixture()
def query_api() -> (
    List[Union[itunes_api.ItunesApiSongModel, itunes_api.ItunesApiAlbumKeys]]
):
    """pytest fixture that queries the itunes search
    api for songs.

    Yields:
        List[Union[itunes_api.ItunesApiSongModel, itunes_api.ItunesApiAlbumKeys]]: a list of songs that match the album
    """
    results = itunes.query_api(
        search_variable="jolene", limit=20, mode=modes.Modes.SONG, lookup=False
    )
    yield results


@pytest.fixture()
def query_api_album() -> (
    List[Union[itunes_api.ItunesApiSongModel, itunes_api.ItunesApiAlbumKeys]]
):
    """pytest fixture that queries the itunes
    search api for an album, and returns
    the songs in that album

    Yields:
        List[Union[itunes_api.ItunesApiSongModel, itunes_api.ItunesApiAlbumKeys]]: the list of song properties
    """
    album_results = itunes.query_api(
        search_variable="jolene", limit=20, mode=modes.Modes.ALBUM, lookup=False
    )
    # select first result by default
    result = album_results[0]
    song_results = itunes.query_api(
        search_variable=result.collectionId,
        limit=result.trackCount,
        mode=modes.Modes.SONG,
        lookup=True,
    )

    yield song_results


def test_query_api(query_api):
    assert len(query_api) > 0


def test_query_api_album(query_api_album):
    assert len(query_api_album) > 0


def test_m4a_tagger(create_test_folder, query_api):
    """test m4a tagging function executes
    successfully
    """
    input_fpath = os.path.join(sys.path[0], RESOURCES_FOLDER, "empty.m4a")
    output_fpath = os.path.join(create_test_folder, "empty.m4a")
    shutil.copy(input_fpath, output_fpath)
    # query api, get the first result
    tags = query_api[0]
    result = itunes.m4a_tagger(file_path=output_fpath, song_tag_data=tags)

    assert result == True


def test_mp3_tagger(create_test_folder, query_api):
    """test mp3 tagging function executes successfully"""
    input_fpath = os.path.join(sys.path[0], RESOURCES_FOLDER, "empty.mp3")
    output_fpath = os.path.join(create_test_folder, "empty.mp3")
    shutil.copy(input_fpath, output_fpath)
    # query api, get the first result
    tags = query_api[0]
    result = itunes.mp3ID3Tagger(mp3_path=output_fpath, song_tag_data=tags)

    assert result == True


@pytest.fixture()
def get_itunes_lib_path():
    return os.path.join(sys.path[0], RESOURCES_FOLDER, "mock-itunes-lib")


def test_itunes_lib_search_default(get_itunes_lib_path):
    """test itunes lib search functionality using mock itunes library"""
    results = itunes.itunes_lib_search(
        itunes_lib_path=get_itunes_lib_path,
        search_parameters="empty",
        album_properties=None,
    )
    assert len(results) > 0


def test_itunes_lib_search_with_props(query_api_album, get_itunes_lib_path):
    """test itunes lib search enhanced with album properties"""
    props = query_api_album[0]
    results = itunes.itunes_lib_search(
        itunes_lib_path=get_itunes_lib_path,
        search_parameters="jolene",
        album_properties=props,
    )
    assert len(results) > 0


def test_artwork_searcher(query_api):
    """test getting artwork url given song properties"""
    response = itunes.artwork_searcher(url=query_api[0].artworkUrl100)
    assert response.status_code == 200
