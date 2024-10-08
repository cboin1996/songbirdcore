from typing import List, Optional, Union
import glob
from pydantic import ValidationError
import requests
from requests import Response
import json
import os, sys
import eyed3
from mutagen.mp4 import MP4, MP4Cover
import logging

from . import common
from .models import itunes_api, modes

logger = logging.getLogger(__name__)


def itunes_lib_search(
    itunes_lib_path: str,
    search_parameters: str,
    album_properties: Optional[itunes_api.ItunesApiAlbumKeys] = None,
) -> List[str]:
    """
    Performs a search on users iTunes library by album, artist and genre

    Args:
        itunes_lib_path (str): path to itunes song library on disk
        search_parameters (str): search term
        album_properties (itunes_api.ItunesApiAlbumKeys): determines whether to do a smarter search based on given album properties

    Returns: a list of songpaths found
    """
    itunes_songs = glob.glob(
        os.path.join(itunes_lib_path, "*", "*", f"*.*"), recursive=True
    )
    matches = []
    for song_path in itunes_songs:
        # song_name_split is list of itunes file path.. artist is -3 from length, song is -1
        song_name_split = song_path.split(os.sep)
        song_name = common.remove_illegal_characters(
            song_name_split[len(song_name_split) - 1].lower()
        )
        album_name = common.remove_illegal_characters(
            song_name_split[len(song_name_split) - 2].lower()
        )
        artist_name = common.remove_illegal_characters(
            song_name_split[len(song_name_split) - 3].lower()
        )
        search_parameters = common.remove_illegal_characters(search_parameters.lower())
        if album_properties == None:
            formatted_name = song_name + " " + album_name + " " + artist_name
            if search_parameters in formatted_name:
                matches.append(song_path)
        else:
            if (
                album_properties.artistName.lower() in artist_name
                and search_parameters in song_name
            ):
                matches.append(song_path)

    # returns sorted alphabetical list of matches.
    matches.sort()
    return matches


def m4a_tagger(file_path: str, song_tag_data: itunes_api.ItunesApiSongModel) -> bool:
    """Tag an m4a file using iTunes recognized tags.

    The below is a tag legend taken from mutagen website.
    Text values:

    ```
    '\\xa9nam' - track title
    '\\xa9alb' - album
    '\\xa9ART' - artist
    'aART' - album artist
    '\\xa9day' - year
    'purd' - purchase date
    '\\xa9gen' - genre
    Tuples of ints (multiple values per key are supported):
    'trkn' - track number, total tracks
    'disk' - disc number, total discs
    'covr' - cover artwork, list of MP4Cover objects (which are tagged strs)
    ```

    Args:
        file_path (str): path to the m4a file
        song_tag_data (itunes_api.ItunesApiSongModel): The model for the songs relevant metadata collected from itunes search api

    Returns:
        bool: true if tagging was successful.
    """
    try:
        logger.info(f"Adding tags to m4a file : {file_path}")

        response = artwork_searcher(url=song_tag_data.artworkUrl100)
        audiofile = MP4(file_path)

        # Set all the tags for the mp3, all without if statement were checked for existence.
        audiofile["\xa9ART"] = song_tag_data.artistName
        audiofile["\xa9alb"] = song_tag_data.collectionName
        audiofile["\xa9nam"] = song_tag_data.trackName
        audiofile["\xa9gen"] = song_tag_data.primaryGenreName
        audiofile["trkn"] = [(song_tag_data.trackNumber, song_tag_data.trackCount)]
        audiofile["disk"] = [(song_tag_data.discNumber, song_tag_data.discCount)]
        audiofile["\xa9day"] = song_tag_data.releaseDate

        if (
            song_tag_data.collectionArtistName is not None
        ):  # check if collection_artist_name exists before adding to tags
            audiofile["aART"] = song_tag_data.collectionArtistName

        if response.status_code == 200:
            audiofile["covr"] = [
                MP4Cover(response.content, imageformat=MP4Cover.FORMAT_PNG)
            ]

        audiofile.save()
        logger.info("Your tags have been set.")
        return True
    except Exception as e:
        logger.exception(
            f"Unexpected error occured while trying to tag your m4a file: {e}"
        )
        return False


def mp3ID3Tagger(mp3_path: str, song_tag_data: itunes_api.ItunesApiSongModel) -> bool:
    """
    Tags an mp3 file at mp3_path given a itunes_api.ItunesApiSongModel object

    Args:
        mp3_path (str): file path of mp3 file
        song_tag_data (itunes_api.ItunesApiSongModel): the model with tag fields

    Returns:
        bool: true if tagging was a success
    """
    try:
        # Create MP3File instance.
        logger.info(f"Adding your tags to mp3 file: {mp3_path}")
        # Have to call MP3File twice for it to work.

        # Get the image to show for a song .. but get high res
        # get album artwork from the list of sizes

        response = artwork_searcher(url=song_tag_data.artworkUrl100)

        # Set all the tags for the mp3, all without if statement were checked for existence.
        audiofile = eyed3.load(mp3_path)
        audiofile.tag.artist = song_tag_data.artistName
        audiofile.tag.album = song_tag_data.collectionName
        audiofile.tag.title = song_tag_data.trackName
        audiofile.tag.genre = song_tag_data.primaryGenreName
        audiofile.tag.track_num = (song_tag_data.trackNumber, song_tag_data.trackCount)
        audiofile.tag.disc_num = (song_tag_data.discNumber, song_tag_data.discCount)
        audiofile.tag.recording_date = song_tag_data.releaseDate

        if (
            song_tag_data.collectionArtistName is not None
        ):  # check if collection_artist_name exists before adding to tags
            audiofile.tag.album_artist = song_tag_data.collectionArtistName

        if response.status_code == 200:
            audiofile.tag.images.set(
                type_=3,
                img_data=response.content,
                mime_type="image/png",
                description="Art",
                img_url=None,
            )

        audiofile.tag.save()
        logger.info("Your tags have been set.")
        return True

    except Exception as e:
        logger.exception(
            f"Unexpected error occured while trying to tag your mp3 file: {e}"
        )
        return False


def query_api(
    search_variable: str, limit: int, mode: modes.Modes, lookup: bool = False
) -> List[Union[itunes_api.ItunesApiSongModel, itunes_api.ItunesApiAlbumKeys]]:
    """
    Args:
        search_variable (str): the term to search itunes api for
        limit  (int): limit of the search in the api
        mode (modes.Modes): value of album, or song for now
        lookup (bool): if true, perform a lookup search via itunes api rather than a default search
    Returns
        List[Union[itunes_api.ItunesApiSongModel, itunes_api.ItunesApiAlbumKeys]]: a list containing a
            tuple with itunes song properties and album properties
    """
    parsed_results_list = []
    result_dict = {}
    if not lookup:  # perform general search
        search_parameters = {
            "term": search_variable,
            "entity": mode.value,
            "limit": limit,
        }
        itunes_response = requests.get(
            "https://itunes.apple.com/search", params=search_parameters
        )
    else:  # perform lookup query by itunes id
        search_parameters = {
            "id": search_variable,
            "entity": mode.value,
            "limit": limit,
        }
        itunes_response = requests.get(
            "https://itunes.apple.com/lookup", params=search_parameters
        )

    # itunesResponse = requests.get('https://itunes.apple.com/search?term=jack+johnson')
    logger.info(f"Connected to {itunes_response.url}")
    if itunes_response.status_code != 200:
        logger.error(
            "Oops. Something went wrong trying to connect to the itunes server."
        )
        logger.error(
            f"Code: {itunes_response.status_code}, Body: {itunes_response.content}"
        )
        return None

    itunes_json_dict = json.loads(itunes_response.content)
    for index, search_result in enumerate(itunes_json_dict["results"]):
        try:
            if mode == modes.Modes.SONG:
                result = itunes_api.ItunesApiSongModel.model_validate(search_result)
                year = search_result[result.releaseDateKey].split("-")[
                    0
                ]  # will grab the year from date formatted 2016-06-01
                result.releaseDate = year
            elif mode == modes.Modes.ALBUM:
                result = itunes_api.ItunesApiAlbumKeys.model_validate(search_result)

            parsed_results_list.append(result)
        except ValidationError as e:
            logger.warning(
                f"Skipping the display of song at index [{index}] as it could not be loaded into expected format.\n{e}"
            )

    return parsed_results_list


def artwork_searcher(url: str) -> Optional[Response]:
    """Album artwork searcher.

    Args:
        url (str): the url for the artwork

    Returns:
        Response: the response for the artwork request
    """
    artwork_size_list = [
        "100x100",
        "500x500",
        "1000x1000",
        "1500x1500",
        "2000x2000",
        "2500x2500",
        "3000x3000",
    ]
    i = len(artwork_size_list) - 1

    response = requests.get(url.replace("100x100", artwork_size_list[i]))
    while response.status_code != 200 and i != 0:
        logger.info(f"- Size not found -- Trying size: {artwork_size_list[i]}")
        response = requests.get(url.replace("100x100", artwork_size_list[i]))
        i -= 1

    if i == 0:
        logger.info("Couldnt find album art. Your file wont have the art.")
        return None

    else:
        logger.info(f"Found art at size: {artwork_size_list[i]}")

    return response
